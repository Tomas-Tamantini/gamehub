from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.api.dependencies.event_bus import T_EventBus
from gamehub.api.dependencies.rooms_factory import default_rooms
from gamehub.core.room_manager import RoomManager


@lru_cache
def get_room_manager(event_bus: T_EventBus) -> RoomManager:
    return RoomManager(rooms=list(default_rooms(event_bus)), event_bus=event_bus)


T_RoomManager = Annotated[RoomManager, Depends(get_room_manager)]
