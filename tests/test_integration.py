import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.game_setup import GameSetup
from gamehub.core.message import MessageEvent, MessageType
from gamehub.core.request import Request, RequestType
from gamehub.core.room_manager import RoomManager
from tests.utils import ExpectedBroadcast, check_messages


@pytest.mark.asyncio
async def test_end_to_end():
    event_bus = EventBus()

    game_room = GameRoom(room_id=1, setup=GameSetup(num_players=2), event_bus=event_bus)
    room_manager = RoomManager([game_room], event_bus)
    event_bus.subscribe(Request, room_manager.handle_request)

    messages: list[MessageEvent] = []
    event_bus.subscribe(MessageEvent, messages.append)

    requests = (
        Request(
            player_id="Alice",
            request_type=RequestType.JOIN_GAME,
            payload={"room_id": 1},
        ),
        Request(
            player_id="Bob",
            request_type=RequestType.JOIN_GAME,
            payload={"room_id": 1},
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
    )

    check_messages(messages, expected_broadcasts)
