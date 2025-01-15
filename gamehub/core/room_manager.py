from pydantic import BaseModel

from gamehub.core.game_room import GameRoom
from gamehub.core.request import Request, RequestType


class _JoinRoomPayload(BaseModel):
    room_id: int


class RoomManager:
    def __init__(self, rooms: list[GameRoom]):
        self._rooms = {room.room_id: room for room in rooms}

    async def handle_request(self, request: Request) -> None:
        if request.request_type == RequestType.JOIN_GAME:
            parsed_payload = _JoinRoomPayload.model_validate(request.payload)
            room = self._rooms[parsed_payload.room_id]
            await room.join(request.player_id)
