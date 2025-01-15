from unittest.mock import AsyncMock, Mock

import pytest

from gamehub.core.message import Message, MessageType
from gamehub.socket_server import ClientManager, ConnectionHandler


@pytest.fixture
def mock_client():
    def _mock_client(client_msg: str):
        mock_client = AsyncMock()
        mock_client.__aiter__.return_value = iter([client_msg])
        return mock_client

    return _mock_client


@pytest.mark.asyncio
async def test_handler_responds_when_unable_to_parse_request(mock_client):
    socket_handler = ConnectionHandler(ClientManager())
    client = mock_client("bad request")
    client.__aiter__.return_value = iter(["bad request"])
    await socket_handler.handle_client(client)
    error_msg = client.send.call_args.args[0]
    parsed_error_msg = Message.model_validate_json(error_msg)
    assert parsed_error_msg.message_type == MessageType.ERROR
    assert "Invalid JSON" in parsed_error_msg.payload


@pytest.mark.asyncio
async def test_handler_keeps_track_of_connected_clients(mock_client):
    client_manager_spy = Mock(spec=ClientManager)
    socket_handler = ConnectionHandler(client_manager_spy)
    client = mock_client('{"request_type":"JOIN_GAME","player_id":"test_id"}')
    await socket_handler.handle_client(client)
    client_manager_spy.associate_player_id.assert_called_once_with("test_id", client)


@pytest.mark.asyncio
async def test_handler_discards_disconnected_clients(mock_client):
    client_manager_spy = Mock(spec=ClientManager)
    socket_handler = ConnectionHandler(client_manager_spy)
    client = mock_client('{"request_type":"JOIN_GAME","player_id":"test_id"}')
    await socket_handler.handle_client(client)
    client_manager_spy.remove.assert_called_once_with(client)
