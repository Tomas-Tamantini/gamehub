import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request import RequestType
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageType
from gamehub.core.room_manager import RoomManager
from gamehub.core.setup_bus import setup_event_bus
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def message_spy():
    class _MessageSenderSpy:
        def __init__(self):
            self.messages = []

        async def send(self, message: OutgoingMessage) -> None:
            self.messages.append(message)

    return _MessageSenderSpy()


@pytest.fixture
def event_bus(message_spy):
    event_bus = EventBus()
    game_room = GameRoom(
        room_id=1,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )
    room_manager = RoomManager([game_room], event_bus)
    setup_event_bus(event_bus, message_spy, room_manager)
    return event_bus


@pytest.fixture
def join_game(build_request):
    return lambda player_id: build_request(
        player_id=player_id,
        request_type=RequestType.JOIN_GAME_BY_ID,
        payload={"room_id": 1},
    )


@pytest.fixture
def watch_game(build_request):
    return lambda player_id: build_request(
        player_id=player_id,
        request_type=RequestType.WATCH_GAME,
        payload={"room_id": 1},
    )


@pytest.fixture
def make_move(build_request):
    return lambda player_id, selection: build_request(
        player_id=player_id,
        request_type=RequestType.MAKE_MOVE,
        payload={"room_id": 1, "move": {"selection": selection}},
    )


@pytest.mark.asyncio
async def test_full_gameplay(message_spy, event_bus, watch_game, make_move, join_game):
    requests = (
        watch_game("Spectator"),
        join_game("Alice"),
        join_game("Bob"),
        make_move("Alice", "ROCK"),
        make_move("Bob", "SCISSORS"),
    )

    for request in requests:
        await event_bus.publish(request)

    expected_broadcasts = (
        ExpectedBroadcast(
            ["Spectator"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 1,
                "capacity": 2,
                "player_ids": [],
                "offline_players": [],
                "is_full": False,
                "configuration": None,
            },
        ),
        ExpectedBroadcast(
            ["Alice", "Spectator"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 1,
                "capacity": 2,
                "player_ids": ["Alice"],
                "offline_players": [],
                "is_full": False,
                "configuration": None,
            },
        ),
        ExpectedBroadcast(
            ["Alice", "Bob", "Spectator"],
            MessageType.GAME_ROOM_UPDATE,
            {
                "room_id": 1,
                "capacity": 2,
                "player_ids": ["Alice", "Bob"],
                "offline_players": [],
                "is_full": True,
                "configuration": None,
            },
        ),
        ExpectedBroadcast(
            ["Alice", "Bob", "Spectator"],
            MessageType.GAME_STATE,
            {
                "room_id": 1,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": False},
                        {"player_id": "Bob", "selected": False},
                    ]
                },
            },
        ),
        ExpectedBroadcast(
            ["Alice"],
            MessageType.GAME_STATE,
            {
                "room_id": 1,
                "private_view": {"selection": "ROCK"},
            },
        ),
        ExpectedBroadcast(
            ["Alice", "Bob", "Spectator"],
            MessageType.GAME_STATE,
            {
                "room_id": 1,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": True},
                        {"player_id": "Bob", "selected": False},
                    ]
                },
            },
        ),
        ExpectedBroadcast(
            ["Alice", "Bob", "Spectator"],
            MessageType.GAME_STATE,
            {
                "room_id": 1,
                "shared_view": {
                    "players": [
                        {"player_id": "Alice", "selected": True},
                        {"player_id": "Bob", "selected": True},
                    ],
                    "result": {
                        "winner": "Alice",
                        "moves": [
                            {"player_id": "Alice", "selection": "ROCK"},
                            {"player_id": "Bob", "selection": "SCISSORS"},
                        ],
                    },
                },
            },
        ),
    )

    check_messages(message_spy.messages, expected_broadcasts)
