from unittest.mock import AsyncMock

import pytest

from gamehub.core.exceptions import AmbiguousPlayerIdError
from gamehub.socket_server import ClientManager


def test_client_manager_associates_client_with_player_id():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("test_id", mock_client)
    assert client_manager.get_client("test_id") == mock_client


def test_client_cannot_have_two_player_ids():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("id_1", mock_client)
    with pytest.raises(
        AmbiguousPlayerIdError, match="already associated with another id"
    ):
        client_manager.associate_player_id("id_2", mock_client)


def test_player_id_cannot_have_two_clients():
    client_manager = ClientManager()
    client_a = AsyncMock()
    client_b = AsyncMock()
    client_manager.associate_player_id("id_1", client_a)
    with pytest.raises(AmbiguousPlayerIdError, match="id already in use"):
        client_manager.associate_player_id("id_1", client_b)


def test_client_manager_removes_client():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.associate_player_id("test_id", mock_client)
    client_manager.remove(mock_client)
    assert client_manager.get_client("test_id") is None


def test_removing_inexistent_client_does_nothing():
    client_manager = ClientManager()
    mock_client = AsyncMock()
    client_manager.remove(mock_client)
