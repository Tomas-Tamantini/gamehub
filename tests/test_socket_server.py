from unittest.mock import AsyncMock

import pytest

from gamehub.core.message import Message, MessageType
from gamehub.socket_server import ClientManager, ConnectionHandler


def test_client_manager_associates_websocket_with_player_id():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("test_id", mock_client)
    assert client_manager.get_client("test_id") == mock_client


def test_client_manager_returns_none_if_no_client_associated_with_id():
    client_manager = ClientManager()
    assert client_manager.get_client("test_id") is None


@pytest.mark.asyncio
async def test_socket_connection_handler_responds_when_unable_to_parse_request():
    socket_handler = ConnectionHandler(ClientManager())
    mock_client = AsyncMock()
    mock_client.__aiter__.return_value = iter(["bad request"])
    await socket_handler.handle_client(mock_client)
    error_msg = mock_client.send.call_args.args[0]
    parsed_error_msg = Message.model_validate_json(error_msg)
    assert parsed_error_msg.message_type == MessageType.ERROR
    assert "Invalid JSON" in parsed_error_msg.payload


@pytest.mark.asyncio
async def test_socket_connection_handler_keeps_track_of_connected_clients():
    client_manager = ClientManager()
    socket_handler = ConnectionHandler(client_manager)
    mock_client = AsyncMock()
    id_request = '{"request_type":"JOIN_GAME","player_id":"test_id"}'
    mock_client.__aiter__.return_value = iter([id_request])
    await socket_handler.handle_client(mock_client)
    assert client_manager.get_client("test_id") == mock_client
