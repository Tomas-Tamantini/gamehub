from pydantic import BaseModel, Field


class SocketRequest(BaseModel):
    player_id: str = Field(min_length=1)
    raw_request: str
