import pytest
from pydantic import BaseModel

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageType
from gamehub.games.chinese_poker import (
    ChinesePokerConfiguration,
    ChinesePokerGameLogic,
    ChinesePokerMove,
)
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def messages_spy(event_bus):
    messages = []
    event_bus.subscribe(OutgoingMessage, messages.append)
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
def chinese_poker_room(event_bus):
    config = ChinesePokerConfiguration(
        num_players=4, cards_per_player=13, game_over_point_threshold=10
    )
    return GameRoom(
        room_id=1,
        game_logic=ChinesePokerGameLogic(config),
        move_parser=ChinesePokerMove.model_validate,
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

        def make_move(self, *_, **__):
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
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Alice"],
                "offline_players": [],
                "is_full": False,
            },
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
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Alice", "Bob"],
                "offline_players": [],
                "is_full": True,
            },
        )
    ]
    check_messages(messages_spy[1:3], expected)


@pytest.mark.asyncio
async def test_room_ignores_disconnected_player_if_not_inside_room(
    rps_room, messages_spy
):
    await rps_room.join("Alice")
    await rps_room.handle_player_disconnected("Bob")
    assert len(messages_spy) == 1


@pytest.mark.asyncio
async def test_room_notifies_other_players_if_one_disconnects(
    chinese_poker_room, messages_spy
):
    await chinese_poker_room.join("Alice")
    await chinese_poker_room.join("Bob")
    await chinese_poker_room.join("Charlie")
    await chinese_poker_room.handle_player_disconnected("Charlie")
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 1,
                "capacity": 4,
                "player_ids": ["Alice", "Bob"],
                "offline_players": [],
                "is_full": False,
            },
        )
    ]
    check_messages(messages_spy[6:], expected)


@pytest.mark.asyncio
async def test_room_does_not_remove_disconnected_player_if_game_has_started(
    chinese_poker_room, messages_spy
):
    await chinese_poker_room.join("Alice")
    await chinese_poker_room.join("Bob")
    await chinese_poker_room.join("Charlie")
    await chinese_poker_room.join("Diana")
    await chinese_poker_room.handle_player_disconnected("Alice")
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob", "Charlie", "Diana"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 1,
                "capacity": 4,
                "player_ids": ["Alice", "Bob", "Charlie", "Diana"],
                "offline_players": ["Alice"],
                "is_full": True,
            },
        )
    ]
    check_messages(messages_spy[-4:], expected)


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
async def test_player_cannot_rejoin_room_they_are_not_in(rps_room, messages_spy):
    await rps_room.rejoin("Alice")

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert messages_spy[-1].message.payload["error"] == "Player not in room"


@pytest.mark.asyncio
async def test_player_cannot_rejoin_room_if_they_were_not_offline(
    rps_room, messages_spy
):
    await rps_room.join("Alice")
    await rps_room.rejoin("Alice")

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert messages_spy[-1].message.payload["error"] == "Player is not offline"


@pytest.mark.asyncio
async def test_players_get_notified_of_player_rejoining(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.handle_player_disconnected("Alice")
    await rps_room.rejoin("Alice")

    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Alice", "Bob"],
                "offline_players": [],
                "is_full": True,
            },
        )
    ]
    check_messages(messages_spy[7:9], expected)


@pytest.mark.asyncio
async def test_players_get_notified_of_full_game_state_when_rejoining(
    rps_room, messages_spy
):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "ROCK"})
    await rps_room.handle_player_disconnected("Alice")
    await rps_room.rejoin("Alice")

    expected = [
        ExpectedBroadcast(
            ["Alice"],
            MessageType.GAME_STATE,
            {
                "room_id": 0,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": True},
                        {"player_id": "Bob", "selected": False},
                    ]
                },
                "private_view": {"selection": "ROCK"},
            },
        )
    ]
    check_messages(messages_spy[12:], expected)


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
    await rps_room.add_spectator("Spec")
    await rps_room.make_move("Alice", {"selection": "ROCK"})
    await rps_room.make_move("Bob", {"selection": "PAPER"})
    await rps_room.join("Charlie")

    expected = [
        ExpectedBroadcast(
            ["Charlie"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Charlie"],
                "offline_players": [],
                "is_full": False,
            },
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


@pytest.mark.asyncio
async def test_spectator_can_watch_room_before_game_starts(rps_room, messages_spy):
    await rps_room.add_spectator("Alice")
    expected = [
        ExpectedBroadcast(
            ["Alice"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": [],
                "offline_players": [],
                "is_full": False,
            },
        )
    ]
    check_messages(messages_spy, expected)


@pytest.mark.asyncio
async def test_spectator_can_watch_room_with_game_in_progress(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.make_move("Alice", {"selection": "ROCK"})
    await rps_room.add_spectator("Charlie")

    expected = [
        ExpectedBroadcast(
            ["Charlie"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Alice", "Bob"],
                "offline_players": [],
                "is_full": True,
            },
        ),
        ExpectedBroadcast(
            ["Charlie"],
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
    check_messages(messages_spy[-2:], expected)


@pytest.mark.asyncio
async def test_spectators_get_notified_of_room_updates(rps_room, messages_spy):
    await rps_room.add_spectator("Alice")
    await rps_room.join("Bob")
    expected = [
        ExpectedBroadcast(
            ["Bob", "Alice"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 0,
                "capacity": 2,
                "player_ids": ["Bob"],
                "offline_players": [],
                "is_full": False,
            },
        )
    ]
    check_messages(messages_spy[-2:], expected)


@pytest.mark.asyncio
async def test_spectators_get_notified_of_game_updates(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.add_spectator("Charlie")
    await rps_room.make_move("Alice", {"selection": "ROCK"})

    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob", "Charlie"],
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
    check_messages(messages_spy[8:], expected)


@pytest.mark.asyncio
async def test_spectators_are_removed_if_they_disconnect(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.join("Bob")
    await rps_room.add_spectator("Charlie")
    await rps_room.handle_player_disconnected("Charlie")
    await rps_room.make_move("Alice", {"selection": "ROCK"})

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
        ),
    ]
    check_messages(messages_spy[8:], expected)


@pytest.mark.asyncio
async def test_spectators_are_removed_if_they_become_players(rps_room, messages_spy):
    await rps_room.add_spectator("Alice")
    await rps_room.join("Alice")
    assert len(messages_spy) == 2


@pytest.mark.asyncio
async def test_players_cannot_join_as_spectators(rps_room, messages_spy):
    await rps_room.join("Alice")
    await rps_room.add_spectator("Alice")
    assert len(messages_spy) == 2

    assert messages_spy[-1].player_id == "Alice"
    assert messages_spy[-1].message.message_type == MessageType.ERROR
    assert (
        messages_spy[-1].message.payload["error"]
        == "Already joined game. Cannot watch as spectator"
    )
