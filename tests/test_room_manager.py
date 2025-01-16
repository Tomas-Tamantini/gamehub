from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.core.request import Request, RequestType
from gamehub.core.room_manager import RoomManager


@pytest.fixture
def spy_room():
    room = Mock(spec=GameRoom)
    room.room_id = 1
    return room


@pytest.fixture
def output_messages(spy_room):
    async def _output_messages(request: Request):
        event_bus = EventBus()
        room_manager = RoomManager([spy_room], event_bus)
        sent_messages = []
        event_bus.subscribe(MessageEvent, sent_messages.append)
        await room_manager.handle_request(request)
        return sent_messages

    return _output_messages


@pytest.mark.parametrize("request_type", [RequestType.JOIN_GAME, RequestType.MAKE_MOVE])
@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_request(
    output_messages, request_type
):
    request = Request(
        player_id="Ana", request_type=request_type, payload={"bad_key": 1}
    )
    sent_messages = await output_messages(request)
    assert len(sent_messages) == 1
    assert sent_messages[0].player_id == "Ana"
    assert sent_messages[0].message.message_type == MessageType.ERROR
    assert "bad_key" in sent_messages[0].message.payload


@pytest.mark.parametrize(
    ("request_type", "payload"),
    [
        (RequestType.JOIN_GAME, {"room_id": 2}),
        (RequestType.MAKE_MOVE, {"room_id": 2, "move": {}}),
    ],
)
@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_room_id(
    output_messages, request_type, payload
):
    request = Request(player_id="Ana", request_type=request_type, payload=payload)
    sent_messages = await output_messages(request)
    assert len(sent_messages) == 1
    assert sent_messages[0].player_id == "Ana"
    assert sent_messages[0].message.message_type == MessageType.ERROR
    assert "id 2 does not exist" in sent_messages[0].message.payload


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room(
    output_messages, spy_room
):
    request = Request(
        player_id="Ana", request_type=RequestType.JOIN_GAME, payload={"room_id": 1}
    )
    _ = await output_messages(request)
    spy_room.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_forwards_make_move_request_to_proper_room(
    output_messages, spy_room
):
    mock_move = {"testkey": "testvalue"}
    request = Request(
        player_id="Ana",
        request_type=RequestType.MAKE_MOVE,
        payload={"room_id": 1, "move": mock_move},
    )
    _ = await output_messages(request)
    spy_room.make_move.assert_called_once_with("Ana", mock_move)
