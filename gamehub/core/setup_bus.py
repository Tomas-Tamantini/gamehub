from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request import Request
from gamehub.core.events.request_events import (
    JoinGameById,
    JoinGameByType,
    MakeMove,
    RejoinGame,
)
from gamehub.core.message_sender import MessageSender
from gamehub.core.request_parser import RequestParser
from gamehub.core.room_manager import RoomManager


def setup_event_bus(
    event_bus: EventBus, message_sender: MessageSender, room_manager: RoomManager
) -> None:
    request_parser = RequestParser(event_bus)
    event_bus.subscribe(Request, request_parser.parse_request)
    event_bus.subscribe(OutgoingMessage, message_sender.send)
    event_bus.subscribe(JoinGameById, room_manager.join_game_by_id)
    event_bus.subscribe(RejoinGame, room_manager.rejoin_game)
    event_bus.subscribe(JoinGameByType, room_manager.join_game_by_type)
    event_bus.subscribe(MakeMove, room_manager.make_move)
    event_bus.subscribe(PlayerDisconnected, room_manager.handle_player_disconnected)
