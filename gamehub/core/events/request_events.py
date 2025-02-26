from pydantic import BaseModel


class DirectedRequest(BaseModel):
    player_id: str
    room_id: int


class JoinGameById(DirectedRequest): ...


class RejoinGame(DirectedRequest): ...


class WatchGame(DirectedRequest): ...


class MakeMove(DirectedRequest):
    move: dict


class JoinGameByType(BaseModel):
    player_id: str
    game_type: str
