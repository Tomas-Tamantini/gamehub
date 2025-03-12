from http import HTTPStatus

from fastapi import APIRouter

from gamehub.api.dependencies import T_RoomManager
from gamehub.api.dto.list_response import ListResponse
from gamehub.core.room_state import RoomState
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms_router.get(
    "/chinese-poker",
    status_code=HTTPStatus.OK,
    response_model=ListResponse[RoomState[ChinesePokerConfiguration]],
)
async def get_rooms(room_manager: T_RoomManager):
    rooms = list(room_manager.room_states(game_type="chinese_poker"))
    return ListResponse[RoomState[ChinesePokerConfiguration]](items=rooms)
