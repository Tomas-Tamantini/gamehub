from enum import Enum

from pydantic import BaseModel, Field


class RequestType(Enum):
    JOIN_GAME_BY_ID = "JOIN_GAME_BY_ID"
    REJOIN_GAME = "REJOIN_GAME"
    JOIN_GAME_BY_TYPE = "JOIN_GAME_BY_TYPE"
    MAKE_MOVE = "MAKE_MOVE"


class Request(BaseModel):
    player_id: str = Field(min_length=1)
    raw_request: str
