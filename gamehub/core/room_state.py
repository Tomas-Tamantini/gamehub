from pydantic import BaseModel


class RoomState(BaseModel):
    room_id: int
    player_ids: list[str]
    offline_players: list[str]
    is_full: bool
