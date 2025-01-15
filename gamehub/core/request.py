from enum import Enum

from pydantic import BaseModel, Field


class RequestType(Enum):
    JOIN_GAME = "JOIN_GAME"


class Request(BaseModel):
    player_id: str = Field(min_length=1)
    request_type: RequestType
    payload: dict = dict()
