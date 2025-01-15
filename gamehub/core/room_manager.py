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

    async def handle_request(self, request: Request) -> None:
        if request.request_type == RequestType.JOIN_GAME:
            try:
                parsed_payload = _JoinRoomPayload.model_validate(request.payload)
                room = self._rooms[parsed_payload.room_id]
                await room.join(request.player_id)
            except ValidationError as e:
                await self._event_bus.publish(
                    MessageEvent(
                        player_id=request.player_id,
                        message=Message(message_type=MessageType.ERROR, payload=str(e)),
                    )
                )
