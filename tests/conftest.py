import json

import pytest

from gamehub.core.events.request import Request, RequestType


@pytest.fixture
def build_request():
    def _build_request(player_id: str, request_type: RequestType, payload: dict):
        raw_request = json.dumps(
            {"request_type": request_type.value, "payload": payload}
        )
        return Request(player_id=player_id, raw_request=raw_request)

    return _build_request
