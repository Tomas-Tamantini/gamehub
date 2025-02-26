from pydantic import BaseModel


class _DirectedRequest(BaseModel):
    player_id: str
    room_id: int


class JoinGameById(_DirectedRequest): ...


class RejoinGame(_DirectedRequest): ...


class WatchGame(_DirectedRequest): ...


class MakeMove(_DirectedRequest):
    move: dict


class JoinGameByType(BaseModel):
    player_id: str
    game_type: str
