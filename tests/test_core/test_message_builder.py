import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_room_update import GameRoomUpdate
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.message import MessageType
from gamehub.core.message_builder import MessageBuilder
from gamehub.core.room_state import RoomState


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
        spectators={"Charlie", "Diana"},
    )
    await msg_builder.broadcast_room_update(room_update)
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
