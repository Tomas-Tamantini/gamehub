import json

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.request import Request, RequestType


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def event_spy(event_bus):
    def _spy(event_type: type):
        events = []
        event_bus.subscribe(event_type, events.append)
        return events

    return _spy


@pytest.fixture
def build_request():
    def _build_request(player_id: str, request_type: RequestType, payload: dict):
        raw_request = json.dumps(
            {"request_type": request_type.value, "payload": payload}
        )
        return Request(player_id=player_id, raw_request=raw_request)

    return _build_request
