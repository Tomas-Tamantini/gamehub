from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById
from gamehub.core.events.make_move import MakeMove
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.core.room_manager import RoomManager


@pytest.fixture
def spy_room():
    room = Mock(spec=GameRoom)
    room.room_id = 1
    return room


async def make_join_game_by_id_request(
    request: JoinGameById, room: GameRoom, messages_spy: list[MessageEvent] = None
):
    event_bus = EventBus()
    room_manager = RoomManager([room], event_bus)
    if messages_spy is not None:
        event_bus.subscribe(MessageEvent, messages_spy.append)
    await room_manager.join_game_by_id(request)


async def make_move_request(
    request: MakeMove, room: GameRoom, messages_spy: list[MessageEvent] = None
):
    event_bus = EventBus()
    room_manager = RoomManager([room], event_bus)
    if messages_spy is not None:
        event_bus.subscribe(MessageEvent, messages_spy.append)
    await room_manager.make_move(request)


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_room_id_when_joining_game(
    spy_room,
):
    request = JoinGameById(player_id="Ana", room_id=2)
    messages_spy = []
    await make_join_game_by_id_request(request, spy_room, messages_spy)
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
    await make_move_request(request, spy_room, messages_spy)
    assert len(messages_spy) == 1
    assert messages_spy[0].player_id == "Ana"
    assert messages_spy[0].message.message_type == MessageType.ERROR
    assert "id 2 does not exist" in messages_spy[0].message.payload["error"]


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room(spy_room):
    request = JoinGameById(player_id="Ana", room_id=1)
    await make_join_game_by_id_request(request, spy_room)
    spy_room.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_forwards_make_move_request_to_proper_room(spy_room):
    mock_move = {"testkey": "testvalue"}
    request = MakeMove(player_id="Ana", room_id=1, move=mock_move)
    await make_move_request(request, spy_room)
    spy_room.make_move.assert_called_once_with("Ana", mock_move)
