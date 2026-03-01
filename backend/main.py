import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from heygen_service import HeyGenService
from models import (
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

    return {"team_id": team_id, "team": team}


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


@app.post("/api/streaming-token")
async def create_streaming_token():
    """Create a short-lived streaming token for the HeyGen Streaming Avatar SDK."""
    try:
        token = await heygen.create_streaming_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen API error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
