from unittest.mock import AsyncMock

import pytest

from gamehub.socket_server import SocketServer


@pytest.mark.asyncio
async def test_socket_server_responds_when_unable_to_parse_request():
    client_request = "bad message"
    socket_handler = SocketServer()
    mock_client = AsyncMock()
    mock_client.__aiter__.return_value = iter([client_request])
    await socket_handler.handle_client(mock_client)
    mock_client.send.assert_called_once_with("Unable to parse request: bad message")
