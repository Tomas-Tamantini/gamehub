from unittest.mock import Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request_events import (
    JoinGameById,
    JoinGameByType,
    MakeMove,
    RejoinGame,
    RequestFailed,
    WatchGame,
)
from gamehub.core.events.timer_events import TurnTimeout
from gamehub.core.game_room import GameRoom
from gamehub.core.room_manager import RoomManager
from gamehub.core.room_state import RoomState


@pytest.fixture
def spy_room():
    def _spy_room(
        room_id: int = 1, is_full: bool = False, game_type: str = "tic-tac-toe"
    ):
        room = Mock(spec=GameRoom)
        room.room_id = room_id
        room.is_full = is_full
        room.game_type = game_type
        room.room_state.return_value = RoomState[str](
            room_id=room_id,
            capacity=2,
            player_ids=["Ana", "Bob"],
            offline_players=[],
            is_full=is_full,
            configuration="config",
        )
        return room

    return _spy_room


@pytest.mark.parametrize(
    ("event", "method_name"),
    [
        (JoinGameById(player_id="Ana", room_id=2), "join_game_by_id"),
        (RejoinGame(player_id="Ana", room_id=2), "rejoin_game"),
        (WatchGame(player_id="Ana", room_id=2), "watch_game"),
        (MakeMove(player_id="Ana", room_id=2, move={}), "make_move"),
    ],
)
@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_room_id(
    spy_room, event, method_name, event_bus, event_spy
):
    request = event
    events = event_spy(RequestFailed)
    room_manager = RoomManager([spy_room()], event_bus)
    await getattr(room_manager, method_name)(request)
    assert len(events) == 1
    assert events[0].player_id == "Ana"
    assert "id 2 does not exist" in events[0].error_msg


@pytest.mark.asyncio
async def test_room_manager_returns_error_message_if_bad_game_type_when_joining_game(
    spy_room, event_bus, event_spy
):
    request = JoinGameByType(player_id="Ana", game_type="tic-tac-toe")
    events = event_spy(RequestFailed)
    room_manager = RoomManager([spy_room(is_full=True)], event_bus)
    await room_manager.join_game_by_type(request)
    assert len(events) == 1
    assert events[0].player_id == "Ana"
    assert "No available" in events[0].error_msg


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room(spy_room):
    request = JoinGameById(player_id="Ana", room_id=1)
    room = spy_room()
    room_manager = RoomManager([room], EventBus())
    await room_manager.join_game_by_id(request)
    room.join.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_forwards_rejoin_game_request_to_proper_room(spy_room):
    request = RejoinGame(player_id="Ana", room_id=1)
    room = spy_room()
    room_manager = RoomManager([room], EventBus())
    await room_manager.rejoin_game(request)
    room.rejoin.assert_called_once_with("Ana")


@pytest.mark.asyncio
async def test_room_manager_forwards_watch_game_request_to_proper_room(spy_room):
    request = WatchGame(player_id="Ana", room_id=1)
    room = spy_room()
    room_manager = RoomManager([room], EventBus())
    await room_manager.watch_game(request)
    room.add_spectator.assert_called_once_with("Ana")


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
async def test_room_manager_notifies_rooms_when_user_disconnects(
    spy_room,
):
    request = PlayerDisconnected(player_id="Ana")
    room = spy_room(room_id=1)
    room_manager = RoomManager([room], EventBus())
    await room_manager.handle_player_disconnected(request)
    room.handle_player_disconnected.assert_called_once_with("Ana")


@pytest.fixture
def example_rooms(spy_room):
    return [
        spy_room(room_id=1, game_type="tic-tac-toe"),
        spy_room(room_id=2, game_type="rock-paper-scissors"),
        spy_room(room_id=3, game_type="tic-tac-toe"),
    ]


@pytest.fixture
def expected_room_states():
    return [
        RoomState[str](
            room_id=1,
            capacity=2,
            player_ids=["Ana", "Bob"],
            offline_players=[],
            is_full=False,
            configuration="config",
        ),
        RoomState[str](
            room_id=2,
            capacity=2,
            player_ids=["Ana", "Bob"],
            offline_players=[],
            is_full=False,
            configuration="config",
        ),
        RoomState[str](
            room_id=3,
            capacity=2,
            player_ids=["Ana", "Bob"],
            offline_players=[],
            is_full=False,
            configuration="config",
        ),
    ]


@pytest.mark.asyncio
async def test_room_manager_returns_all_room_states_if_no_filter(
    example_rooms, expected_room_states
):
    event_bus = EventBus()
    room_manager = RoomManager(example_rooms, event_bus)
    room_states = list(room_manager.room_states())
    assert room_states == expected_room_states


@pytest.mark.asyncio
async def test_room_manager_returns_room_states_filtered_by_game_type(
    example_rooms, expected_room_states
):
    event_bus = EventBus()
    room_manager = RoomManager(example_rooms, event_bus)
    room_states = list(room_manager.room_states(game_type="tic-tac-toe"))
    assert room_states == [expected_room_states[0], expected_room_states[2]]


@pytest.mark.asyncio
async def test_room_manager_ignores_timeout_event_if_no_room_matches_id(spy_room):
    room = spy_room(room_id=1)
    room_manager = RoomManager([room], EventBus())
    event = TurnTimeout(room_id=2, player_id="Ana", recipients=[])
    await room_manager.handle_timeout(event)
    spy_room().handle_timeout.assert_not_called()


@pytest.mark.asyncio
async def test_room_manager_forwards_timeout_event_to_proper_room(spy_room):
    room = spy_room(room_id=1)
    room_manager = RoomManager([room], EventBus())
    event = TurnTimeout(room_id=1, player_id="Ana", recipients=[])
    await room_manager.handle_timeout(event)
    room.handle_timeout.assert_called_once_with("Ana")
