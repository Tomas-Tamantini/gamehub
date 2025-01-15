from unittest.mock import Mock

import pytest

from gamehub.core.game_room import GameRoom
from gamehub.core.request import Request, RequestType
from gamehub.core.room_manager import RoomManager


@pytest.mark.asyncio
async def test_room_manager_forwards_join_game_request_to_proper_room():
    spy_room = Mock(spec=GameRoom)
    spy_room.room_id = 1
    manager = RoomManager([spy_room])
    request = Request(
        player_id="Ana", request_type=RequestType.JOIN_GAME, payload={"room_id": 1}
    )
    await manager.handle_request(request)
    spy_room.join.assert_called_once_with("Ana")
