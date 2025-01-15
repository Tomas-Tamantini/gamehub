from gamehub.core.game_room import GameRoom
from gamehub.core.event_bus import EventBus
from gamehub.core.message import MessageEvent, MessageType, Message
import pytest


@pytest.mark.asyncio
async def test_player_can_join_empty_room():
    event_bus = EventBus()
    sent_messages = []
    event_bus.subscribe(MessageEvent, sent_messages.append)
    room = GameRoom(room_id=0, event_bus=event_bus)
    await room.join("Alice")
    assert len(sent_messages) == 1
    assert sent_messages[0].player_id == "Alice"
    assert sent_messages[0].message.message_type == MessageType.PLAYER_JOINED
    assert sent_messages[0].message.payload == '{"room_id": 0, "player_ids": ["Alice"]}'


@pytest.mark.asyncio
async def test_players_get_informed_when_new_one_joins():
    event_bus = EventBus()
    sent_messages = []
    event_bus.subscribe(MessageEvent, sent_messages.append)
    room = GameRoom(room_id=0, event_bus=event_bus)
    await room.join("Alice")
    await room.join("Bob")
    assert len(sent_messages) == 3
    assert sent_messages[1].player_id == "Alice"
    assert sent_messages[1].message.message_type == MessageType.PLAYER_JOINED
    assert (
        sent_messages[1].message.payload
        == '{"room_id": 0, "player_ids": ["Alice", "Bob"]}'
    )
    assert sent_messages[2].player_id == "Bob"
    assert sent_messages[2].message.message_type == MessageType.PLAYER_JOINED
    assert (
        sent_messages[2].message.payload
        == '{"room_id": 0, "player_ids": ["Alice", "Bob"]}'
    )
