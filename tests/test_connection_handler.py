import json
from typing import Optional
from unittest.mock import AsyncMock, Mock

import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.request import Request, RequestType
from gamehub.core.message import Message, MessageType
from gamehub.socket_server import ClientManager, ConnectionHandler


@pytest.fixture
def valid_request():
    return lambda player_id: json.dumps(
        {
            "request_type": "JOIN_GAME_BY_ID",
            "player_id": player_id,
        }
    )


@pytest.fixture
def client(valid_request):
    request = valid_request("test_id")
    mock_client = AsyncMock()
    mock_client.__aiter__.return_value = iter([request])
    return mock_client


@pytest.fixture
def bad_request_client():
    client = AsyncMock()
    client.__aiter__.return_value = iter(["bad request"])
    return client


@pytest.fixture
def duplicate_id_client(valid_request):
    req_1 = valid_request("id_1")
    req_2 = valid_request("id_2")
    client = AsyncMock()
    client.__aiter__.return_value = iter([req_1, req_2])
    return client


@pytest.fixture
def connection_handler():
    def _handler(
        client_manager: Optional[ClientManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        client_manager = client_manager or ClientManager()
        event_bus = event_bus or EventBus()
        return ConnectionHandler(client_manager, event_bus)

    return _handler


@pytest.mark.asyncio
async def test_handler_responds_when_unable_to_parse_request(
    connection_handler, bad_request_client
):
    await connection_handler().handle_client(bad_request_client)
    error_msg = bad_request_client.send.call_args.args[0]
    parsed_error_msg = Message.model_validate_json(error_msg)
    assert parsed_error_msg.message_type == MessageType.ERROR
    assert "Invalid JSON" in parsed_error_msg.payload["error"]


@pytest.mark.asyncio
async def test_handler_keeps_track_of_connected_clients(connection_handler, client):
    client_manager_spy = Mock(spec=ClientManager)
    await connection_handler(client_manager_spy).handle_client(client)
    client_manager_spy.associate_player_id.assert_called_once_with("test_id", client)


@pytest.mark.asyncio
async def test_handler_discards_disconnected_clients(connection_handler, client):
    client_manager_spy = Mock(spec=ClientManager)
    await connection_handler(client_manager_spy).handle_client(client)
    client_manager_spy.remove.assert_called_once_with(client)


@pytest.mark.asyncio
async def test_handler_publishes_request_in_event_bus(connection_handler, client):
    event_bus = EventBus()
    requests = []
    event_bus.subscribe(Request, requests.append)
    await connection_handler(event_bus=event_bus).handle_client(client)
    assert len(requests) == 1
    assert requests[0].request_type == RequestType.JOIN_GAME_BY_ID
    assert requests[0].player_id == "test_id"


@pytest.mark.asyncio
async def test_handler_returns_error_if_same_client_has_two_ids(
    connection_handler, duplicate_id_client
):
    await connection_handler().handle_client(duplicate_id_client)
    error_msg = duplicate_id_client.send.call_args.args[0]
    parsed_error_msg = Message.model_validate_json(error_msg)
    assert parsed_error_msg.message_type == MessageType.ERROR
    assert "already associated with another id" in parsed_error_msg.payload["error"]
