import asyncio
from dataclasses import dataclass, field

import pytest

from gamehub.core.event_bus import EventBus


@dataclass(frozen=True)
class _OrderPlaced:
    order_id: int


@dataclass(frozen=True)
class _OrderCancelled:
    order_id: int


@dataclass
class _HandlerSpy:
    received_events: list = field(default_factory=list)

    def handle_sync(self, event):
        self.received_events.append(event)

    async def handle_async(self, event):
        self.received_events.append(event)
        await asyncio.sleep(0.001)


@pytest.mark.asyncio
async def test_event_bus_publishes_event_to_subscribed_handlers():
    bus = EventBus()
    spy = _HandlerSpy()
    event = _OrderPlaced(order_id=1)
    bus.subscribe(_OrderPlaced, spy.handle_sync)
    await bus.publish(event)
    assert spy.received_events == [event]


@pytest.mark.asyncio
async def test_event_bus_does_not_publish_event_to_unsubscribed_handlers():
    bus = EventBus()
    spy = _HandlerSpy()
    event = _OrderPlaced(order_id=5)
    bus.subscribe(_OrderCancelled, spy.handle_sync)
    await bus.publish(event)
    assert spy.received_events == []


@pytest.mark.asyncio
async def test_event_bus_can_have_multiple_handlers_for_same_event():
    bus = EventBus()

    spy_a = _HandlerSpy()
    bus.subscribe(_OrderCancelled, spy_a.handle_sync)

    spy_b = _HandlerSpy()
    bus.subscribe(_OrderCancelled, spy_b.handle_sync)

    event = _OrderCancelled(order_id=2)
    await bus.publish(event)

    assert spy_a.received_events == [event]
    assert spy_b.received_events == [event]


@pytest.mark.asyncio
async def test_event_bus_can_have_multiple_events_for_same_handler():
    bus = EventBus()

    spy = _HandlerSpy()
    bus.subscribe(_OrderCancelled, spy.handle_sync)
    bus.subscribe(_OrderPlaced, spy.handle_sync)

    event_a = _OrderCancelled(order_id=3)
    await bus.publish(event_a)

    event_b = _OrderPlaced(order_id=4)
    await bus.publish(event_b)

    assert spy.received_events == [event_a, event_b]


@pytest.mark.asyncio
async def test_event_bus_can_have_async_handlers():
    bus = EventBus()
    spy = _HandlerSpy()
    event = _OrderPlaced(order_id=1)
    bus.subscribe(_OrderPlaced, spy.handle_async)
    await bus.publish(event)
    assert spy.received_events == [event]
