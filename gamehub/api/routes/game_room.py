from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter

from gamehub.api.dependencies import T_RoomManager
from gamehub.api.dto.list_response import ListResponse
from gamehub.core.room_state import RoomState

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms_router.get(
    "/", status_code=HTTPStatus.OK, response_model=ListResponse[RoomState]
)
async def get_rooms(room_manager: T_RoomManager, game_type: Optional[str] = None):
    rooms = list(room_manager.room_states(game_type))
    return ListResponse[RoomState](items=rooms)
