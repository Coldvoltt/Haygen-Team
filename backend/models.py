from pydantic import BaseModel


class TeamMember(BaseModel):
    name: str
    intro_text: str


class TeamCreateRequest(BaseModel):
    team_name: str
    members: list[TeamMember]


class TeamCreateData(BaseModel):
    """Parsed from the JSON string in the multipart form."""
    team_name: str
    members: list[TeamMember]


class GenerateIntroRequest(BaseModel):
    team_id: str
    member_index: int


class StoredMember(BaseModel):
    name: str
    intro_text: str
    avatar_type: str = "avatar"  # "avatar" or "talking_photo"
    avatar_id: str | None = None
    avatar_name: str = ""
    avatar_preview_image: str = ""
    talking_photo_id: str | None = None
    voice_id: str
    video_id: str | None = None
    video_url: str | None = None
    video_status: str | None = None


class StoredTeam(BaseModel):
    team_id: str
    team_name: str
    members: list[StoredMember]
