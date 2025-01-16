from gamehub.core.event_bus import EventBus
from gamehub.core.message import MessageEvent
from gamehub.core.message_sender import MessageSender
from gamehub.core.request import Request
from gamehub.core.room_manager import RoomManager


def setup_event_bus(
    event_bus: EventBus, message_sender: MessageSender, room_manager: RoomManager
) -> None:
    event_bus.subscribe(Request, room_manager.handle_request)
    event_bus.subscribe(MessageEvent, message_sender.send)
