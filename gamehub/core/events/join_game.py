from pydantic import BaseModel


class JoinGameById(BaseModel):
    player_id: str
    room_id: int


class RejoinGame(BaseModel):
    player_id: str
    room_id: int


class JoinGameByType(BaseModel):
    player_id: str
    game_type: str
