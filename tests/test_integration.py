import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent, MessageType
from gamehub.core.request import Request, RequestType
from gamehub.core.room_manager import RoomManager
from gamehub.core.setup_bus import setup_event_bus
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from tests.utils import ExpectedBroadcast, check_messages


class _MessageSenderSpy:
    def __init__(self):
        self.messages = []

    async def send(self, message: MessageEvent) -> None:
        self.messages.append(message)


@pytest.mark.asyncio
async def test_integration():
    message_spy = _MessageSenderSpy()
    event_bus = EventBus()

    game_room = GameRoom(
        room_id=1,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )
    room_manager = RoomManager([game_room], event_bus)
    setup_event_bus(event_bus, message_spy, room_manager)

    requests = (
        Request(
            player_id="Alice",
            request_type=RequestType.JOIN_GAME_BY_ID,
            payload={"room_id": 1},
        ),
        Request(
            player_id="Bob",
            request_type=RequestType.JOIN_GAME_BY_ID,
            payload={"room_id": 1},
        ),
        Request(
            player_id="Alice",
            request_type=RequestType.MAKE_MOVE,
            payload={"room_id": 1, "move": {"selection": "ROCK"}},
        ),
        Request(
            player_id="Bob",
            request_type=RequestType.MAKE_MOVE,
            payload={"room_id": 1, "move": {"selection": "SCISSORS"}},
        ),
    )

    for request in requests:
        await event_bus.publish(request)

    expected_broadcasts = (
        ExpectedBroadcast(
            ["Alice"],
            MessageType.PLAYER_JOINED,
            {"room_id": 1, "player_ids": ["Alice"]},
        ),
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.PLAYER_JOINED,
            {"room_id": 1, "player_ids": ["Alice", "Bob"]},
        ),
        ExpectedBroadcast(
            ["Alice", "Bob"],
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
            ["Alice", "Bob"],
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
            ["Alice", "Bob"],
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
