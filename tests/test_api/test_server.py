from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket

from gamehub.server import websocket_endpoint


@pytest.mark.asyncio
async def test_server_forwards_socket_clients_to_connection_handler():
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_handler = AsyncMock()
    await websocket_endpoint(mock_websocket, mock_handler)
    mock_handler.handle_client.assert_awaited_once_with(mock_websocket)
