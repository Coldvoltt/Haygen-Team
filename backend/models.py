from pydantic import BaseModel


class TeamMember(BaseModel):
    name: str
    intro_text: str


class TeamCreateRequest(BaseModel):
    team_name: str
    members: list[TeamMember]


class StoredMember(BaseModel):
    name: str
    intro_text: str
    avatar_id: str
    avatar_name: str
    avatar_preview_image: str
    voice_id: str


class StoredTeam(BaseModel):
    team_id: str
    team_name: str
    members: list[StoredMember]
