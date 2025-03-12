from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class RoomState(BaseModel, Generic[T]):
    room_id: int
    capacity: int
    player_ids: list[str]
    offline_players: list[str]
    is_full: bool
    configuration: Optional[T] = None
