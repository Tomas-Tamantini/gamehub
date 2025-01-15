from unittest.mock import AsyncMock

from gamehub.socket_server import ClientManager


def test_client_manager_associates_client_with_player_id():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("test_id", mock_client)
    assert client_manager.get_client("test_id") == mock_client


def test_client_manager_removes_client():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("test_id", mock_client)
    client_manager.remove(mock_client)
    assert client_manager.get_client("test_id") is None
