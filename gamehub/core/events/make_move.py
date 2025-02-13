from pydantic import BaseModel


class MakeMove(BaseModel):
    player_id: str
    room_id: int
    move: dict
