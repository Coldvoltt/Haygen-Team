from pydantic import BaseModel


class TeamMember(BaseModel):
    name: str
    intro_text: str


class TeamCreateRequest(BaseModel):
    team_name: str
    members: list[TeamMember]


class GenerateIntroRequest(BaseModel):
    team_id: str
    member_index: int


class StoredMember(BaseModel):
    name: str
    intro_text: str
    avatar_id: str
    avatar_name: str
    avatar_preview_image: str
    voice_id: str
    video_id: str | None = None
    video_url: str | None = None
    video_status: str | None = None


class StoredTeam(BaseModel):
    team_id: str
    team_name: str
    members: list[StoredMember]
