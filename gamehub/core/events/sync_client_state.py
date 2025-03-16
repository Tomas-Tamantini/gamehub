from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from gamehub.core.room_state import RoomState

T = TypeVar("T")


@dataclass(frozen=True)
class SyncClientState(Generic[T]):
    client_id: str
    room_state: RoomState[T]
    shared_view: Optional[BaseModel] = None
    private_view: Optional[BaseModel] = None
