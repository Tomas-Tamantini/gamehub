from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.api.dependencies.client_manager import T_ClientManager
from gamehub.api.dependencies.event_bus import T_EventBus
from gamehub.api.dependencies.message_sender import T_MessageSender
from gamehub.api.dependencies.room_manager import T_RoomManager
from gamehub.api.dependencies.turn_timer_registry import T_TurnTimerRegistry
from gamehub.api.socket_server import ConnectionHandler
from gamehub.core.setup_bus import setup_event_bus


@lru_cache
def get_connection_handler(
    event_bus: T_EventBus,
    client_manager: T_ClientManager,
    message_sender: T_MessageSender,
    room_manager: T_RoomManager,
    turn_timer_registry: T_TurnTimerRegistry,
) -> ConnectionHandler:
    setup_event_bus(event_bus, message_sender, room_manager, turn_timer_registry)
    return ConnectionHandler(client_manager, event_bus)


T_ConnectionHandler = Annotated[ConnectionHandler, Depends(get_connection_handler)]
