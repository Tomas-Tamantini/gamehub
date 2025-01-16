from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent
from gamehub.core.message_sender import MessageSender
from gamehub.core.request import Request
from gamehub.core.room_manager import RoomManager
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove


def setup_event_bus(message_sender: MessageSender) -> EventBus:
    event_bus = EventBus()
    game_room = GameRoom(
        room_id=1,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )
    room_manager = RoomManager([game_room], event_bus)
    event_bus.subscribe(Request, room_manager.handle_request)

    event_bus.subscribe(MessageEvent, message_sender.send)

    return event_bus
