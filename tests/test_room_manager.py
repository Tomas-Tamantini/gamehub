from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.core.request import Request, RequestType
from gamehub.core.room_manager import RoomManager


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room():
    spy_room = Mock(spec=GameRoom)
    spy_room.room_id = 1
    manager = RoomManager([spy_room], EventBus())
    request = Request(
        player_id="Ana", request_type=RequestType.JOIN_GAME, payload={"room_id": 1}
    )
    await manager.handle_request(request)
    spy_room.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_request():
    sent_messages = []
    event_bus = EventBus()
    event_bus.subscribe(MessageEvent, sent_messages.append)
    manager = RoomManager([], event_bus)
    request = Request(
        player_id="Ana", request_type=RequestType.JOIN_GAME, payload={"bad_key": 1}
    )
    await manager.handle_request(request)
    assert len(sent_messages) == 1
    assert sent_messages[0].player_id == "Ana"
    assert sent_messages[0].message.message_type == MessageType.ERROR
    assert "bad_key" in sent_messages[0].message.payload
