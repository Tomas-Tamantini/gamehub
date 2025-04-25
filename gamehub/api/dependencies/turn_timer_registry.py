from functools import lru_cache
from typing import Annotated, Iterator

from fastapi import Depends

from gamehub.api.dependencies.event_bus import T_EventBus
from gamehub.core.event_bus import EventBus
from gamehub.core.turn_timer import EventScheduler, TurnTimer, TurnTimerRegistry


def _create_turn_timer(event_bus: EventBus, room_id: int) -> TurnTimer:
    return TurnTimer(
        event_scheduler=EventScheduler(event_bus),
        room_id=room_id,
        timeout_seconds=60,
        reminders_at_seconds_remaining=[30, 5],
    )


def _turn_timers(event_bus: EventBus) -> Iterator[TurnTimer]:
    for room_id in (1, 2, 3):
        yield _create_turn_timer(event_bus, room_id)


@lru_cache
def get_turn_timer_registry(event_bus: T_EventBus) -> TurnTimerRegistry:
    return TurnTimerRegistry(turn_timers=list(_turn_timers(event_bus)))


T_TurnTimerRegistry = Annotated[TurnTimerRegistry, Depends(get_turn_timer_registry)]
