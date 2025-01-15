from typing import Optional

from pydantic import BaseModel, ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import Message, MessageEvent, MessageType
from gamehub.core.request import Request, RequestType


class _JoinRoomPayload(BaseModel):
    room_id: int


class RoomManager:
    def __init__(self, rooms: list[GameRoom], event_bus: EventBus):
        self._rooms = {room.room_id: room for room in rooms}
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, message: str) -> None:
        await self._event_bus.publish(
            MessageEvent(
                player_id=player_id,
                message=Message(message_type=MessageType.ERROR, payload=message),
            )
        )

    async def _parse_payload(self, request: Request) -> Optional[_JoinRoomPayload]:
        try:
            return _JoinRoomPayload.model_validate(request.payload)
        except ValidationError as e:
            await self._respond_error(request.player_id, str(e))

    async def handle_request(self, request: Request) -> None:
        if request.request_type == RequestType.JOIN_GAME:
            if parsed_payload := await self._parse_payload(request):
                if not (room := self._rooms.get(parsed_payload.room_id)):
                    await self._respond_error(
                        request.player_id,
                        f"Room with id {parsed_payload.room_id} does not exist",
                    )
                else:
                    await room.join(request.player_id)
