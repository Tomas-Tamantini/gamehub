from typing import Awaitable, Callable

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def output_messages():
    async def _output_messages(action: Callable[[GameRoom], Awaitable[None]]):
        event_bus = EventBus()
        sent_messages = []
        event_bus.subscribe(MessageEvent, sent_messages.append)
        room = GameRoom(
            room_id=0,
            game_logic=RPSGameLogic(),
            move_parser=RPSMove.model_validate,
            event_bus=event_bus,
        )
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
            {
                "room_id": 0,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": False},
                        {"player_id": "Bob", "selected": False},
                    ]
                },
            },
        )
    ]
    check_messages(sent_messages[3:], expected)


@pytest.mark.asyncio
async def test_players_gets_informed_of_new_game_state_after_making_move(
    output_messages,
):
    async def _action(room: GameRoom):
        await room.join("Alice")
        await room.join("Bob")
        await room.make_move("Alice", {"selection": "ROCK"})

    sent_messages = await output_messages(_action)
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_STATE,
            {
                "room_id": 0,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": True},
                        {"player_id": "Bob", "selected": False},
                    ]
                },
            },
        )
    ]
    check_messages(sent_messages[5:], expected)


# TODO:
# Check private view after move
# Check move parse error
# Check invalid move error
