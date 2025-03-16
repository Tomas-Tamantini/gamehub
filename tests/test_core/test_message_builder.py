import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.message import MessageType
from gamehub.core.message_builder import MessageBuilder


@pytest.mark.asyncio
async def test_message_builder_notifies_failed_request():
    events_spy = []
    event_bus = EventBus()
    event_bus.subscribe(OutgoingMessage, events_spy.append)
    msg_builder = MessageBuilder(event_bus)
    failed_request = RequestFailed(player_id="Alice", error_msg="Invalid move")
    await msg_builder.build_error_message(failed_request)
    assert len(events_spy) == 1
    assert events_spy[0].message.message_type == MessageType.ERROR
    assert events_spy[0].player_id == "Alice"
    assert events_spy[0].message.payload["error"] == "Invalid move"
