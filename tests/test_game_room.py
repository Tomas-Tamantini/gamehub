from typing import Awaitable, Callable
from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.game_setup import GameSetup
from gamehub.core.game_state import GameState
from gamehub.core.message import MessageEvent, MessageType
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def game_setup():
    initial_game_state = Mock(spec=GameState)
    initial_game_state.shared_view.return_value = {"test_key": "test_value"}
    return GameSetup(num_players=2, initial_state=lambda _: initial_game_state)


@pytest.fixture
def output_messages(game_setup):
    async def _output_messages(action: Callable[[GameRoom], Awaitable[None]]):
        event_bus = EventBus()
        sent_messages = []
        event_bus.subscribe(MessageEvent, sent_messages.append)
        room = GameRoom(room_id=0, setup=game_setup, event_bus=event_bus)
        await action(room)
        return sent_messages

    return _output_messages


@pytest.mark.asyncio
async def test_player_can_join_empty_room(output_messages):
    async def _action(room: GameRoom):
        await room.join("Alice")

    sent_messages = await output_messages(_action)
    expected = [
        ExpectedBroadcast(
            ["Alice"],
            MessageType.PLAYER_JOINED,
            {"room_id": 0, "player_ids": ["Alice"]},
        )
    ]
    check_messages(sent_messages, expected)


@pytest.mark.asyncio
async def test_players_get_informed_when_new_one_joins(output_messages):
    async def _action(room: GameRoom):
        await room.join("Alice")
        await room.join("Bob")

    sent_messages = await output_messages(_action)
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.PLAYER_JOINED,
            {"room_id": 0, "player_ids": ["Alice", "Bob"]},
        )
    ]
    check_messages(sent_messages[1:3], expected)


@pytest.mark.asyncio
async def test_player_cannot_join_full_room(output_messages):
    async def _action(room: GameRoom):
        await room.join("Alice")
        await room.join("Bob")
        await room.join("Charlie")

    sent_messages = await output_messages(_action)
    assert sent_messages[-1].player_id == "Charlie"
    assert sent_messages[-1].message.message_type == MessageType.ERROR
    assert sent_messages[-1].message.payload == "Unable to join: Room is full"


@pytest.mark.asyncio
async def test_player_cannot_join_room_twice(output_messages):
    async def _action(room: GameRoom):
        await room.join("Alice")
        await room.join("Alice")

    sent_messages = await output_messages(_action)
    assert sent_messages[-1].player_id == "Alice"
    assert sent_messages[-1].message.message_type == MessageType.ERROR
    assert sent_messages[-1].message.payload == "Player already in room"


@pytest.mark.asyncio
async def test_game_starts_when_room_is_full(output_messages):
    async def _action(room: GameRoom):
        await room.join("Alice")
        await room.join("Bob")

    sent_messages = await output_messages(_action)
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_STATE,
            {"room_id": 0, "shared_view": {"test_key": "test_value"}},
        )
    ]
    check_messages(sent_messages[3:], expected)
