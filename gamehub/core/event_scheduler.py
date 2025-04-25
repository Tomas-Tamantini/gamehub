import asyncio

from gamehub.core.event_bus import EventBus


class EventScheduler:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    def schedule_event(self, event: any, delay_seconds: int) -> asyncio.Task:
        async def schedule_event():
            await asyncio.sleep(delay_seconds)
            await self._event_bus.publish(event)

        return asyncio.create_task(schedule_event())

    @staticmethod
    def cancel_event(task: asyncio.Task) -> None:
        if not task.done():
            task.cancel()
