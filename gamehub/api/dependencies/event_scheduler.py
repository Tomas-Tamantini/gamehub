from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.api.dependencies.event_bus import T_EventBus
from gamehub.core.event_scheduler import EventScheduler


@lru_cache
def get_event_scheduler(event_bus: T_EventBus) -> EventScheduler:
    return EventScheduler(event_bus)


T_EventScheduler = Annotated[EventScheduler, Depends(get_event_scheduler)]
