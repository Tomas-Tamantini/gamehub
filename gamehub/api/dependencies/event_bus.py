from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.core.event_bus import EventBus


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()


T_EventBus = Annotated[EventBus, Depends(get_event_bus)]
