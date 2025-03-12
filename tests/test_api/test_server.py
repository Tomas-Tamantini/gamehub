from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

from gamehub.api.dependencies.room_manager import get_room_manager
from gamehub.api.routes.socket import websocket_endpoint
from gamehub.core.room_manager import RoomManager
from gamehub.core.room_state import RoomState
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.server import app


def test_health_check_returns_status_ok(client):
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_server_forwards_socket_clients_to_connection_handler():
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_handler = AsyncMock()
    await websocket_endpoint(mock_websocket, mock_handler, player_id="Alice")
    mock_handler.handle_client.assert_awaited_once_with(mock_websocket, "Alice")


@pytest.fixture
def mock_room_manager():
    manager = Mock(spec=RoomManager)
    manager.room_states.return_value = [
        RoomState[ChinesePokerConfiguration](
            room_id=1,
            capacity=2,
            player_ids=["Ana", "Bob"],
            offline_players=[],
            is_full=True,
            configuration=ChinesePokerConfiguration(
                num_players=4, cards_per_player=13, game_over_point_threshold=25
            ),
        ),
        RoomState[ChinesePokerConfiguration](
            room_id=2,
            capacity=3,
            player_ids=["Alice"],
            offline_players=["Alice"],
            is_full=False,
            configuration=ChinesePokerConfiguration(
                num_players=3, cards_per_player=10, game_over_point_threshold=15
            ),
        ),
    ]
    return manager


@pytest.fixture
def client(mock_room_manager):
    with TestClient(app) as client:
        app.dependency_overrides[get_room_manager] = lambda: mock_room_manager
        yield client
        app.dependency_overrides.clear()


def test_getting_chinese_poker_rooms_returns_status_ok(client):
    assert client.get("/rooms/chinese-poker").status_code == 200


def test_getting_chinese_poker_rooms_returns_list_of_game_rooms(client):
    assert client.get("/rooms/chinese-poker").json() == {
        "items": [
            {
                "room_id": 1,
                "capacity": 2,
                "player_ids": ["Ana", "Bob"],
                "offline_players": [],
                "is_full": True,
                "configuration": {
                    "num_players": 4,
                    "cards_per_player": 13,
                    "game_over_point_threshold": 25,
                },
            },
            {
                "room_id": 2,
                "capacity": 3,
                "player_ids": ["Alice"],
                "offline_players": ["Alice"],
                "is_full": False,
                "configuration": {
                    "num_players": 3,
                    "cards_per_player": 10,
                    "game_over_point_threshold": 15,
                },
            },
        ]
    }


def test_getting_chinese_poker_rooms_can_filter_rooms_by_game_type(
    client, mock_room_manager
):
    _ = client.get("/rooms/chinese-poker")
    mock_room_manager.room_states.assert_called_once_with(game_type="chinese_poker")
