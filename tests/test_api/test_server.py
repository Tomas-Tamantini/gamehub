from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

from gamehub.api.dependencies.room_manager import get_room_manager
from gamehub.core.room_manager import RoomManager
from gamehub.core.room_state import RoomState
from gamehub.server import app, websocket_endpoint


@pytest.mark.asyncio
async def test_server_forwards_socket_clients_to_connection_handler():
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_handler = AsyncMock()
    await websocket_endpoint(mock_websocket, mock_handler)
    mock_handler.handle_client.assert_awaited_once_with(mock_websocket)


@pytest.fixture
def mock_room_manager():
    manager = Mock(spec=RoomManager)
    manager.room_states.return_value = [
        RoomState(
            room_id=1, player_ids=["Ana", "Bob"], offline_players=[], is_full=True
        ),
        RoomState(
            room_id=2, player_ids=["Alice"], offline_players=["Alice"], is_full=False
        ),
    ]
    return manager


@pytest.fixture
def client(mock_room_manager):
    with TestClient(app) as client:
        app.dependency_overrides[get_room_manager] = lambda: mock_room_manager
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def get_rooms_response(client):
    return client.get("/rooms?game_type=rock-paper-scissors")


def test_getting_game_rooms_returns_status_ok(get_rooms_response):
    assert get_rooms_response.status_code == 200


def test_getting_game_rooms_filters_room_by_game_type(
    get_rooms_response, mock_room_manager
):
    _ = get_rooms_response
    mock_room_manager.room_states.assert_called_once_with("rock-paper-scissors")


def test_getting_game_rooms_returns_list_of_game_rooms(get_rooms_response):
    assert get_rooms_response.json() == {
        "rooms": [
            {
                "room_id": 1,
                "player_ids": ["Ana", "Bob"],
                "offline_players": [],
                "is_full": True,
            },
            {
                "room_id": 2,
                "player_ids": ["Alice"],
                "offline_players": ["Alice"],
                "is_full": False,
            },
        ]
    }
