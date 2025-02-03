from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById, JoinGameByType
from gamehub.core.events.make_move import MakeMove
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageType
from gamehub.core.room_manager import RoomManager


@pytest.fixture
def spy_room():
    def _spy_room(
        room_id: int = 1, is_full: bool = False, game_type: str = "tic-tac-toe"
    ):
        room = Mock(spec=GameRoom)
        room.room_id = room_id
        room.is_full = is_full
        room.game_type = game_type
        return room

    return _spy_room


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_room_id_when_joining_game(
    spy_room,
):
    request = JoinGameById(player_id="Ana", room_id=2)
    messages_spy = []
    event_bus = EventBus()
    room_manager = RoomManager([spy_room()], event_bus)
    event_bus.subscribe(OutgoingMessage, messages_spy.append)
    await room_manager.join_game_by_id(request)
    assert len(messages_spy) == 1
    assert messages_spy[0].player_id == "Ana"
    assert messages_spy[0].message.message_type == MessageType.ERROR
    assert "id 2 does not exist" in messages_spy[0].message.payload["error"]


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_room_id_when_making_move(
    spy_room,
):
    request = MakeMove(player_id="Ana", room_id=2, move={})
    messages_spy = []
    event_bus = EventBus()
    room_manager = RoomManager([spy_room()], event_bus)
    event_bus.subscribe(OutgoingMessage, messages_spy.append)
    await room_manager.make_move(request)
    assert len(messages_spy) == 1
    assert messages_spy[0].player_id == "Ana"
    assert messages_spy[0].message.message_type == MessageType.ERROR
    assert "id 2 does not exist" in messages_spy[0].message.payload["error"]


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_game_type_when_joining_game(
    spy_room,
):
    request = JoinGameByType(player_id="Ana", game_type="tic-tac-toe")
    messages_spy = []
    event_bus = EventBus()
    room_manager = RoomManager([spy_room(is_full=True)], event_bus)
    event_bus.subscribe(OutgoingMessage, messages_spy.append)
    await room_manager.join_game_by_type(request)
    assert len(messages_spy) == 1
    assert messages_spy[0].player_id == "Ana"
    assert messages_spy[0].message.message_type == MessageType.ERROR
    assert "No available" in messages_spy[0].message.payload["error"]


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room(spy_room):
    request = JoinGameById(player_id="Ana", room_id=1)
    room = spy_room()
    room_manager = RoomManager([room], EventBus())
    await room_manager.join_game_by_id(request)
    room.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_forwards_make_move_request_to_proper_room(spy_room):
    mock_move = {"testkey": "testvalue"}
    request = MakeMove(player_id="Ana", room_id=1, move=mock_move)
    room = spy_room()
    room_manager = RoomManager([room], EventBus())
    await room_manager.make_move(request)
    room.make_move.assert_called_once_with("Ana", mock_move)


@pytest.mark.asyncio
async def test_room_manager_finds_first_non_full_room_of_given_game_type(spy_room):
    request = JoinGameByType(player_id="Ana", game_type="tic-tac-toe")
    room_a = spy_room(room_id=1, is_full=False, game_type="rock-paper-scissors")
    room_b = spy_room(room_id=2, is_full=True, game_type="tic-tac-toe")
    room_c = spy_room(room_id=3, is_full=False, game_type="tic-tac-toe")
    room_manager = RoomManager([room_a, room_b, room_c], EventBus())
    await room_manager.join_game_by_type(request)
    room_a.join.assert_not_called()
    room_b.join.assert_not_called()
    room_c.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_notifies_rooms_with_given_player_when_they_disconnect(
    spy_room,
):
    request = PlayerDisconnected(player_id="Ana")
    room = spy_room(room_id=1)
    room_manager = RoomManager([room], EventBus())
    await room_manager.handle_player_disconnected(request)
    room.handle_player_disconnected.assert_called_once_with("Ana")
