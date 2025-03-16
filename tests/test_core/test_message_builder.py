import pytest
from pydantic import BaseModel

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_room_update import GameRoomUpdate
from gamehub.core.events.game_state_update import GameStateUpdate
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.message import MessageType
from gamehub.core.message_builder import MessageBuilder
from gamehub.core.room_state import RoomState
from tests.utils import ExpectedBroadcast, check_messages


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def messages_spy(event_bus):
    messages = []
    event_bus.subscribe(OutgoingMessage, messages.append)
    return messages


@pytest.mark.asyncio
async def test_message_builder_notifies_failed_request(event_bus, messages_spy):
    msg_builder = MessageBuilder(event_bus)
    failed_request = RequestFailed(player_id="Alice", error_msg="Invalid move")
    await msg_builder.build_error_message(failed_request)
    assert len(messages_spy) == 1
    assert messages_spy[0].message.message_type == MessageType.ERROR
    assert messages_spy[0].player_id == "Alice"
    assert messages_spy[0].message.payload["error"] == "Invalid move"


@pytest.mark.asyncio
async def test_message_builder_broadcasts_game_room_updates_to_recipients(
    event_bus, messages_spy
):
    msg_builder = MessageBuilder(event_bus)
    room_update = GameRoomUpdate(
        room_state=RoomState(
            room_id=123,
            capacity=4,
            player_ids=["Alice", "Bob"],
            offline_players=[],
            is_full=False,
            configuration=None,
        ),
        recipients=["Alice", "Bob", "Charlie", "Diana"],
    )
    await msg_builder.notify_room_update(room_update)
    assert len(messages_spy) == 4
    recipients = {event.player_id for event in messages_spy}
    assert recipients == {"Alice", "Bob", "Charlie", "Diana"}
    assert all(
        event.message.message_type == MessageType.GAME_ROOM_UPDATE
        for event in messages_spy
    )
    assert all(
        event.message.payload == room_update.room_state.model_dump()
        for event in messages_spy
    )


@pytest.mark.asyncio
async def test_message_builder_broadcasts_game_room_updates_to_players_and_spectators(
    event_bus, messages_spy
):
    msg_builder = MessageBuilder(event_bus)
    room_update = GameRoomUpdate(
        room_state=RoomState(
            room_id=123,
            capacity=4,
            player_ids=["Alice", "Bob"],
            offline_players=[],
            is_full=False,
            configuration=None,
        ),
        recipients=["Alice", "Bob", "Charlie", "Diana"],
    )
    await msg_builder.notify_room_update(room_update)
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob", "Charlie", "Diana"],
            MessageType.GAME_ROOM_UPDATE,
            room_update.room_state.model_dump(),
        )
    ]
    check_messages(messages_spy, expected)


class _MockView(BaseModel):
    field: str


@pytest.mark.asyncio
async def test_message_builder_broadcasts_game_state_updates_to_players_and_spectators(
    event_bus, messages_spy
):
    msg_builder = MessageBuilder(event_bus)
    game_update = GameStateUpdate(
        room_id=123,
        shared_view=_MockView(field="value"),
        private_views=dict(),
        recipients=["Alice", "Bob"],
    )
    await msg_builder.notify_game_state_update(game_update)
    expected = [
        ExpectedBroadcast(
            ["Alice", "Bob"],
            MessageType.GAME_STATE,
            {"room_id": 123, "shared_view": {"field": "value"}},
        )
    ]
    check_messages(messages_spy, expected)


@pytest.mark.asyncio
async def test_message_builder_sends_private_game_states_to_players(
    event_bus, messages_spy
):
    msg_builder = MessageBuilder(event_bus)
    game_update = GameStateUpdate(
        room_id=123,
        shared_view=_MockView(field="value"),
        private_views={
            "Alice": _MockView(field="Alice's view"),
            "Bob": _MockView(field="Bob's view"),
        },
        recipients=[],
    )
    await msg_builder.notify_game_state_update(game_update)
    assert len(messages_spy) == 2
    assert all(
        event.message.message_type == MessageType.GAME_STATE for event in messages_spy
    )
    assert all(event.message.payload["room_id"] == 123 for event in messages_spy)
    if messages_spy[0].player_id == "Alice":
        alice_msg, bob_msg = messages_spy
    else:
        bob_msg, alice_msg = messages_spy

    assert alice_msg.player_id == "Alice"
    assert alice_msg.message.payload["private_view"]["field"] == "Alice's view"

    assert bob_msg.player_id == "Bob"
    assert bob_msg.message.payload["private_view"]["field"] == "Bob's view"
