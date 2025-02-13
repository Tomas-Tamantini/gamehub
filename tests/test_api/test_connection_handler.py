import json
from itertools import cycle
from typing import Optional
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocket, WebSocketDisconnect

from gamehub.api.socket_server import ClientManager, ConnectionHandler
from gamehub.core.event_bus import EventBus
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request import Request
from gamehub.core.message import Message, MessageType


@pytest.fixture
def valid_request():
    return json.dumps({"request_type": "JOIN_GAME_BY_ID", "player_id": "Alice"})


@pytest.fixture
def mock_client():
    mock_client = AsyncMock(spec=WebSocket)
    mock_client.accept = AsyncMock()
    return mock_client


@pytest.fixture
def valid_client(mock_client, valid_request):
    mock_client.receive_text = AsyncMock(
        side_effect=[valid_request, WebSocketDisconnect]
    )
    return mock_client


@pytest.fixture
def infinite_loop_client(mock_client, valid_request):
    mock_client.receive_text = AsyncMock(side_effect=cycle([valid_request]))
    return mock_client


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
async def test_handler_keeps_track_of_connected_clients(
    connection_handler, valid_client
):
    client_manager_spy = Mock(spec=ClientManager)
    await connection_handler(client_manager_spy).handle_client(valid_client, "Alice")
    client_manager_spy.associate_player_id.assert_called_once_with(
        "Alice", valid_client
    )


@pytest.mark.asyncio
async def test_handler_discards_disconnected_clients(connection_handler, valid_client):
    client_manager_spy = Mock(spec=ClientManager)
    await connection_handler(client_manager_spy).handle_client(valid_client, "Alice")
    client_manager_spy.remove.assert_called_once_with(valid_client)


@pytest.mark.asyncio
async def test_handler_raises_disconnected_client_event(
    connection_handler, valid_client
):
    client_manager_spy = Mock(spec=ClientManager)
    client_manager_spy.remove.return_value = "Alice"
    events = []
    event_bus = EventBus()
    event_bus.subscribe(PlayerDisconnected, events.append)
    handler = connection_handler(client_manager_spy, event_bus=event_bus)
    await handler.handle_client(valid_client, "Alice")
    assert events == [PlayerDisconnected(player_id="Alice")]


@pytest.mark.asyncio
async def test_handler_publishes_request_in_event_bus(
    connection_handler, valid_client, valid_request
):
    event_bus = EventBus()
    requests = []
    event_bus.subscribe(Request, requests.append)
    await connection_handler(event_bus=event_bus).handle_client(valid_client, "Alice")
    assert len(requests) == 1
    assert requests[0].player_id == "Alice"
    assert requests[0].raw_request == valid_request


@pytest.mark.asyncio
async def test_handler_informs_client_of_bad_player_id(
    connection_handler, infinite_loop_client
):
    bad_player_id = " "
    await connection_handler().handle_client(infinite_loop_client, bad_player_id)
    error_msg = infinite_loop_client.send_text.call_args.args[0]
    parsed_error_msg = Message.model_validate_json(error_msg)
    assert parsed_error_msg.message_type == MessageType.ERROR
    assert "cannot be empty" in parsed_error_msg.payload["error"]


@pytest.mark.asyncio
async def test_handler_closes_connection_if_bad_player_id(
    connection_handler, infinite_loop_client
):
    bad_player_id = " "
    await connection_handler().handle_client(infinite_loop_client, bad_player_id)
    infinite_loop_client.close.assert_called_once()
