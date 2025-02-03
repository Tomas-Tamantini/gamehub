from enum import Enum

from pydantic import BaseModel, Field


class RequestType(Enum):
    JOIN_GAME_BY_ID = "JOIN_GAME_BY_ID"
    JOIN_GAME_BY_TYPE = "JOIN_GAME_BY_TYPE"
    MAKE_MOVE = "MAKE_MOVE"
    QUERY_ROOMS = "QUERY_ROOMS"


class Request(BaseModel):
    player_id: str = Field(min_length=1)
    request_type: RequestType
    payload: dict = dict()


class JoinGameByIdPayload(BaseModel):
    room_id: int


class JoinGameByTypePayload(BaseModel):
    game_type: str


class MakeMovePayload(BaseModel):
    room_id: int
    move: dict


class QueryRoomsPayload(BaseModel):
    game_type: str
