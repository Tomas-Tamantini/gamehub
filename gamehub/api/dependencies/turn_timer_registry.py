from functools import lru_cache
from typing import Annotated, Iterator

from fastapi import Depends

from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


def _turn_timers() -> Iterator[TurnTimer]:
    yield TurnTimer(room_id=1)
    yield TurnTimer(room_id=2)
    yield TurnTimer(room_id=3)


@lru_cache
def get_turn_timer_registry() -> TurnTimerRegistry:
    return TurnTimerRegistry(turn_timers=list(_turn_timers()))


T_TurnTimerRegistry = Annotated[TurnTimerRegistry, Depends(get_turn_timer_registry)]
