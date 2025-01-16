from typing import Optional

from pydantic import BaseModel, ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import Message, MessageEvent, MessageType
from gamehub.core.request import Request, RequestType


class _JoinGamePayload(BaseModel):
    room_id: int


class _MakeMovePayload(BaseModel):
    room_id: int
    move: dict


class RoomManager:
    def __init__(self, rooms: list[GameRoom], event_bus: EventBus):
        self._rooms = {room.room_id: room for room in rooms}
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, message: str) -> None:
        await self._event_bus.publish(
            MessageEvent(
                player_id=player_id,
                message=Message(
                    message_type=MessageType.ERROR, payload={"error": message}
                ),
            )
        )

    async def _parse_request(
        self, request: Request
    ) -> Optional[_JoinGamePayload | _MakeMovePayload]:
        model_cls = (
            _JoinGamePayload
            if request.request_type == RequestType.JOIN_GAME
            else _MakeMovePayload
        )
        try:
            return model_cls.model_validate(request.payload)
        except ValidationError as e:
            await self._respond_error(request.player_id, str(e))

    # TODO: Extract request handler to different class
    async def handle_request(self, request: Request) -> None:
        if parsed_payload := await self._parse_request(request):
            if not (room := self._rooms.get(parsed_payload.room_id)):
                await self._respond_error(
                    request.player_id,
                    f"Room with id {parsed_payload.room_id} does not exist",
                )
            elif isinstance(parsed_payload, _JoinGamePayload):
                await room.join(request.player_id)
            elif isinstance(parsed_payload, _MakeMovePayload):
                await room.make_move(request.player_id, parsed_payload.move)
