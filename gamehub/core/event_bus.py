import asyncio
from collections import defaultdict
from typing import Awaitable, Callable, Type, TypeVar

E = TypeVar("E")
S = Callable[[E], None]
A = Callable[[E], Awaitable[None]]


class EventBus:
    def __init__(self):
        self._sync_handlers = defaultdict(list)
        self._async_handlers = defaultdict(list)

    def subscribe(self, event_type: Type[E], handler: S | A) -> None:
        if asyncio.iscoroutinefunction(handler):
            self._async_handlers[event_type].append(handler)
        else:
            self._sync_handlers[event_type].append(handler)

    async def publish(self, event: E) -> None:
        event_type = type(event)
        for sync_handler in self._sync_handlers[event_type]:
            sync_handler(event)
        for async_handler in self._async_handlers[event_type]:
            await async_handler(event)
