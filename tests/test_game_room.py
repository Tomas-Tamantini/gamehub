import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.game_setup import GameSetup
from gamehub.core.message import MessageEvent, MessageType


@pytest.mark.asyncio
async def test_player_can_join_empty_room():
    event_bus = EventBus()
    sent_messages = []
    event_bus.subscribe(MessageEvent, sent_messages.append)
    room = GameRoom(room_id=0, setup=GameSetup(num_players=2), event_bus=event_bus)
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
    room = GameRoom(room_id=0, setup=GameSetup(num_players=2), event_bus=event_bus)
    await room.join("Alice")
    await room.join("Bob")
    assert len(sent_messages) == 3
    last_messages = sent_messages[-2:]
    assert set(m.player_id for m in last_messages) == {"Alice", "Bob"}
    assert all(
        m.message.message_type == MessageType.PLAYER_JOINED for m in last_messages
    )
    assert all(
        m.message.payload == '{"room_id": 0, "player_ids": ["Alice", "Bob"]}'
        for m in last_messages
    )


@pytest.mark.asyncio
async def test_player_cannot_join_full_room():
    event_bus = EventBus()
    sent_messages = []
    event_bus.subscribe(MessageEvent, sent_messages.append)
    room = GameRoom(room_id=0, setup=GameSetup(num_players=2), event_bus=event_bus)
    await room.join("Alice")
    await room.join("Bob")
    await room.join("Charlie")
    assert len(sent_messages) == 4
    assert sent_messages[-1].player_id == "Charlie"
    assert sent_messages[-1].message.message_type == MessageType.ERROR
    assert sent_messages[-1].message.payload == "Unable to join: Room is full"


@pytest.mark.asyncio
async def test_player_cannot_join_room_twice():
    event_bus = EventBus()
    sent_messages = []
    event_bus.subscribe(MessageEvent, sent_messages.append)
    room = GameRoom(room_id=0, setup=GameSetup(num_players=2), event_bus=event_bus)
    await room.join("Alice")
    await room.join("Alice")
    assert len(sent_messages) == 2
    assert sent_messages[-1].player_id == "Alice"
    assert sent_messages[-1].message.message_type == MessageType.ERROR
    assert sent_messages[-1].message.payload == "Player already in room"
