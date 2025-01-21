import pytest
from pydantic import BaseModel

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def messages_spy(event_bus):
    messages = []
    event_bus.subscribe(MessageEvent, messages.append)
    return messages


@pytest.fixture
def rps_room(event_bus):
    return GameRoom(
        room_id=0,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )


@pytest.fixture
def automated_transition_logic():
    class MockState(BaseModel):
        status: str

        def private_views(self):
            yield from []

        def shared_view(self):
            return self

        def is_terminal(self):
            return False

    class MockLogic:
        @property
        def num_players(self):
            return 2

        def initial_state(self, *_, **__):
            return MockState(status="START")

        def make_move(self, state, *_, **__):
            return MockState(status="MOVE")

        def next_automated_state(self, state, *_, **__):
            if "_" not in state.status:
                return MockState(status="AUTO_" + state.status + "_A")
            elif state.status.endswith("_A"):
                return MockState(status=state.status.replace("_A", "_B"))

    return MockLogic()


@pytest.fixture
def automated_transition_room(event_bus, automated_transition_logic):
    return GameRoom(
        room_id=0,
        game_logic=automated_transition_logic,
        move_parser=lambda _: {"a": 1},
        event_bus=event_bus,
    )


@pytest.mark.asyncio
async def test_player_can_join_empty_room(rps_room, messages_spy):
    await rps_room.join("Alice")
    expected = [
        ExpectedBroadcast(
            ["Alice"],
            MessageType.PLAYER_JOINED,
            {"room_id": 0, "player_ids": ["Alice"]},
        )
    ]
    check_messages(messages_spy, expected)


@pytest.mark.asyncio
async def test_players_get_informed_when_new_one_joins(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.PLAYER_JOINED,
            {"room_id": 0, "player_ids": ["Alice", "Bob"]},
        )
    ]
    check_messages(messages_spy[1:3], expected)


@pytest.mark.asyncio
async def test_player_cannot_join_full_room(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.join("Charlie")

    assert messages_spy[-1].player_id == "Charlie"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert messages_spy[-1].message.payload["error"] == "Unable to join: Room is full"


@pytest.mark.asyncio
async def test_player_cannot_join_room_twice(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Alice")

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert messages_spy[-1].message.payload["error"] == "Player already in room"


@pytest.mark.asyncio
async def test_player_cannot_make_move_before_game_start(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.make_move("Alice", {"selection": "ROCK"})

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert messages_spy[-1].message.payload["error"] == "Game has not started yet"


@pytest.mark.asyncio
async def test_game_starts_when_room_is_full(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")

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
    check_messages(messages_spy[3:], expected)


@pytest.mark.asyncio
async def test_players_get_informed_of_new_game_state_after_making_move(
    rps_room, messages_spy
):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "ROCK"})

    expected = [
        ExpectedBroadcast(
            ["Alice"],
            MessageType.GAME_STATE,
            {
                "room_id": 0,
                "private_view": {"selection": "ROCK"},
            },
        ),
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
        ),
    ]
    check_messages(messages_spy[5:], expected)


@pytest.mark.asyncio
async def test_player_gets_informed_of_parse_move_error(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "bad_value"})

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert "selection" in messages_spy[-1].message.payload["error"]


@pytest.mark.asyncio
async def test_player_gets_informed_of_invalid_move_error(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "ROCK"})
    await rps_room.make_move("Alice", {"selection": "PAPER"})

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert "already selected" in messages_spy[-1].message.payload["error"]


@pytest.mark.asyncio
async def test_player_not_in_game_room_cannot_make_move(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Charlie", {"selection": "ROCK"})

    assert messages_spy[-1].player_id == "Charlie"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert "not in room" in messages_spy[-1].message.payload["error"]


@pytest.mark.asyncio
async def test_game_room_resets_after_game_over_and_new_players_can_join(
    rps_room, messages_spy
):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "ROCK"})
    await rps_room.make_move("Bob", {"selection": "PAPER"})
    await rps_room.join("Charlie")

    expected = [
        ExpectedBroadcast(
            ["Charlie"],
            MessageType.PLAYER_JOINED,
            {"room_id": 0, "player_ids": ["Charlie"]},
        )
    ]
    check_messages(messages_spy[-1:], expected)


def test_room_has_associated_game_type(rps_room):
    assert rps_room.game_type == "rock_paper_scissors"


@pytest.mark.asyncio
async def test_players_get_informed_of_new_game_state_after_automatic_transition(
    automated_transition_room, messages_spy
):
    await automated_transition_room.join("Alice")
    await automated_transition_room.join("Bob")
    await automated_transition_room.make_move("Alice", {})

    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_STATE,
            {"room_id": 0, "shared_view": {"status": status}},
        )
        for status in (
            "START",
            "AUTO_START_A",
            "AUTO_START_B",
            "MOVE",
            "AUTO_MOVE_A",
            "AUTO_MOVE_B",
        )
    ]
    check_messages(messages_spy[3:], expected)
