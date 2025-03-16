from dataclasses import dataclass
from typing import Generic, Iterable, TypeVar

from gamehub.core.room_state import RoomState

T = TypeVar("T")


@dataclass(frozen=True)
class GameRoomUpdate(Generic[T]):
    room_state: RoomState[T]
    spectators: Iterable[str]
