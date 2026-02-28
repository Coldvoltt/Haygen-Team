import asyncio
import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from heygen_service import HeyGenService
from models import (
    GenerateIntroRequest,
    StoredMember,
    StoredTeam,
    TeamCreateRequest,
)

logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("HEYGEN_API_KEY")
if not API_KEY:
    raise RuntimeError("HEYGEN_API_KEY not set. Copy .env.example to .env and add your key.")

app = FastAPI(title="Team Avatar App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

heygen = HeyGenService(API_KEY)

# In-memory store (replace with a DB for production)
teams_db: dict[str, StoredTeam] = {}


@app.get("/api/avatars")
async def get_avatars():
    """List available HeyGen avatars."""
    try:
        avatars = await heygen.list_avatars()
        return {
            "count": len(avatars),
            "avatars": [
                {
                    "avatar_id": a["avatar_id"],
                    "avatar_name": a.get("avatar_name", ""),
                    "gender": a.get("gender", ""),
                    "preview_image_url": a.get("preview_image_url", ""),
                }
                for a in avatars
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen API error: {str(e)}")


@app.post("/api/team")
async def create_team(req: TeamCreateRequest):
    """Create a team and assign random avatars to each member."""
    try:
        avatars = await heygen.list_avatars()
        voices = await heygen.list_voices()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen API error: {str(e)}")

    if not avatars:
        raise HTTPException(status_code=502, detail="No avatars available from HeyGen")

    picked = heygen.pick_random_avatars(avatars, len(req.members))

    stored_members = []
    for member, avatar in zip(req.members, picked):
        voice_id = heygen.get_default_voice_id(avatar, voices)
        stored_members.append(
            StoredMember(
                name=member.name,
                intro_text=member.intro_text,
                avatar_id=avatar["avatar_id"],
                avatar_name=avatar.get("avatar_name", "Unknown"),
                avatar_preview_image=avatar.get("preview_image_url", ""),
                voice_id=voice_id,
            )
        )

    team_id = str(uuid.uuid4())
    team = StoredTeam(
        team_id=team_id,
        team_name=req.team_name,
        members=stored_members,
    )
    teams_db[team_id] = team

    # Pre-generate videos for all members in the background
    asyncio.create_task(_generate_all_videos(team))

    return {"team_id": team_id, "team": team}


async def _generate_all_videos(team: StoredTeam):
    """Fire off video generation for every member concurrently."""
    print(f"[BG] Starting pre-generation for {len(team.members)} members in '{team.team_name}'")
    tasks = []
    for member in team.members:
        tasks.append(_generate_video_for_member(member))
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"[BG] All generation requests sent for '{team.team_name}'")


async def _generate_video_for_member(member: StoredMember):
    """Generate a single member's intro video."""
    try:
        print(f"[BG] Requesting video for {member.name} (avatar: {member.avatar_id})...")
        video_id = await heygen.generate_video(
            avatar_id=member.avatar_id,
            voice_id=member.voice_id,
            input_text=member.intro_text,
            title=f"{member.name} - Introduction",
        )
        member.video_id = video_id
        member.video_status = "pending"
        print(f"[BG] Video queued for {member.name}: video_id={video_id}")
    except Exception as e:
        member.video_status = "failed"
        print(f"[BG] FAILED for {member.name}: {e}")


@app.get("/api/team/{team_id}")
async def get_team(team_id: str):
    """Get a team by ID."""
    team = teams_db.get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"team": team}


@app.get("/api/teams")
async def list_teams():
    """List all teams."""
    return {
        "teams": [
            {"team_id": t.team_id, "team_name": t.team_name, "member_count": len(t.members)}
            for t in teams_db.values()
        ]
    }


@app.post("/api/generate-intro")
async def generate_intro(req: GenerateIntroRequest):
    """Check video status for a team member. Videos are pre-generated at team creation."""
    team = teams_db.get(req.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if req.member_index < 0 or req.member_index >= len(team.members):
        raise HTTPException(status_code=400, detail="Invalid member index")

    member = team.members[req.member_index]

    # Already have the video URL cached
    if member.video_url:
        return {
            "video_id": member.video_id,
            "video_url": member.video_url,
            "status": "completed",
            "member_name": member.name,
        }

    # Video generation was kicked off — check latest status from HeyGen
    if member.video_id:
        try:
            status_data = await heygen.get_video_status(member.video_id)
            current_status = status_data.get("status", "unknown")
            member.video_status = current_status
            if current_status == "completed":
                member.video_url = status_data.get("video_url")
            return {
                "video_id": member.video_id,
                "video_url": member.video_url,
                "status": current_status,
                "member_name": member.name,
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"HeyGen API error: {str(e)}")

    # Edge case: video generation hasn't started yet (e.g. API was slow)
    return {
        "video_id": None,
        "video_url": None,
        "status": "pending",
        "member_name": member.name,
    }


@app.get("/api/video-status/{video_id}")
async def get_video_status(video_id: str):
    """Check the status of a video generation."""
    try:
        status_data = await heygen.get_video_status(video_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen API error: {str(e)}")

    status = status_data.get("status", "unknown")
    video_url = status_data.get("video_url")

    # Update stored member if we find a match
    for team in teams_db.values():
        for member in team.members:
            if member.video_id == video_id:
                member.video_status = status
                if status == "completed" and video_url:
                    member.video_url = video_url
                break

    return {
        "video_id": video_id,
        "status": status,
        "video_url": video_url,
        "thumbnail_url": status_data.get("thumbnail_url"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
