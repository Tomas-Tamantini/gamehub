from http import HTTPStatus

from fastapi import APIRouter
from pydantic import BaseModel

from gamehub.api.dependencies import T_RoomManager
from gamehub.core.room_state import RoomState

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


class GetRoomsResponse(BaseModel):
    items: list[RoomState]


@rooms_router.get("/", status_code=HTTPStatus.OK, response_model=GetRoomsResponse)
async def get_rooms(room_manager: T_RoomManager, game_type: str):
    rooms = list(room_manager.room_states(game_type))
    return GetRoomsResponse(items=rooms)
