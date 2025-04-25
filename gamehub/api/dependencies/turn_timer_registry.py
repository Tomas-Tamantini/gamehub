from functools import lru_cache
from typing import Annotated, Iterator

from fastapi import Depends

from gamehub.api.dependencies.event_scheduler import T_EventScheduler
from gamehub.core.event_scheduler import EventScheduler
from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


def _create_turn_timer(event_scheduler: EventScheduler, room_id: int) -> TurnTimer:
    return TurnTimer(
        event_scheduler=event_scheduler,
        room_id=room_id,
        timeout_seconds=60,
        reminders_at_seconds_remaining=[30, 5],
    )


def _turn_timers(event_scheduler: EventScheduler) -> Iterator[TurnTimer]:
    for room_id in (1, 2, 3):
        yield _create_turn_timer(event_scheduler, room_id)


@lru_cache
def get_turn_timer_registry(event_scheduler: T_EventScheduler) -> TurnTimerRegistry:
    return TurnTimerRegistry(turn_timers=list(_turn_timers(event_scheduler)))


T_TurnTimerRegistry = Annotated[TurnTimerRegistry, Depends(get_turn_timer_registry)]
