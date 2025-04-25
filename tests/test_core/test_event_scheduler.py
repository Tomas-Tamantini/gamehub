import asyncio
from dataclasses import dataclass

import pytest

from gamehub.core.event_scheduler import EventScheduler


@dataclass(frozen=True)
class EventStub:
    event_id: str


@pytest.fixture
def mock_event_spy(event_spy):
    return event_spy(EventStub)


@pytest.mark.asyncio
async def test_event_scheduler_publishes_event(event_bus, mock_event_spy):
    scheduler = EventScheduler(event_bus)
    event = EventStub(event_id="test_event")
    delay_seconds = 0
    scheduler.schedule_event(event, delay_seconds)
    await asyncio.sleep(delay_seconds + 0.1)
    assert mock_event_spy == [event]


@pytest.mark.asyncio
async def test_event_scheduler_allows_cancellation(event_bus, mock_event_spy):
    scheduler = EventScheduler(event_bus)
    event = EventStub(event_id="test_event")
    delay_seconds = 0
    task = scheduler.schedule_event(event, delay_seconds)
    scheduler.cancel_event(task)
    await asyncio.sleep(delay_seconds + 0.1)
    assert mock_event_spy == []
