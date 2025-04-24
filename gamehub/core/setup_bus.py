from typing import Optional

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_room_update import GameRoomUpdate
from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    GameStateUpdate,
    TurnEnded,
    TurnStarted,
)
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request import Request
from gamehub.core.events.request_events import (
    JoinGameById,
    JoinGameByType,
    MakeMove,
    RejoinGame,
    RequestFailed,
    WatchGame,
)
from gamehub.core.events.sync_client_state import SyncClientState
from gamehub.core.message_builder import MessageBuilder
from gamehub.core.message_sender import MessageSender
from gamehub.core.request_parser import RequestParser
from gamehub.core.room_manager import RoomManager
from gamehub.core.turn_timer import TurnTimerRegistry


def setup_event_bus(
    event_bus: EventBus,
    message_sender: MessageSender,
    room_manager: RoomManager,
    timekeeper: Optional[TurnTimerRegistry] = None,
) -> None:
    request_parser = RequestParser(event_bus)
    message_builder = MessageBuilder(event_bus)
    event_bus.subscribe(Request, request_parser.parse_request)
    event_bus.subscribe(RequestFailed, message_builder.build_error_message)
    event_bus.subscribe(GameRoomUpdate, message_builder.notify_room_update)
    event_bus.subscribe(GameStateUpdate, message_builder.notify_game_state_update)
    event_bus.subscribe(SyncClientState, message_builder.sync_client_state)
    event_bus.subscribe(OutgoingMessage, message_sender.send)
    event_bus.subscribe(JoinGameById, room_manager.join_game_by_id)
    event_bus.subscribe(RejoinGame, room_manager.rejoin_game)
    event_bus.subscribe(WatchGame, room_manager.watch_game)
    event_bus.subscribe(JoinGameByType, room_manager.join_game_by_type)
    event_bus.subscribe(MakeMove, room_manager.make_move)
    event_bus.subscribe(PlayerDisconnected, room_manager.handle_player_disconnected)
    if timekeeper:
        event_bus.subscribe(GameStarted, timekeeper.handle_game_start)
        event_bus.subscribe(GameEnded, timekeeper.handle_game_end)
        event_bus.subscribe(TurnStarted, timekeeper.handle_turn_start)
        event_bus.subscribe(TurnEnded, timekeeper.handle_turn_end)
