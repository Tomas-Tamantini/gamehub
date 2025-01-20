from typing import Optional

from pydantic import ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById
from gamehub.core.events.make_move import MakeMove
from gamehub.core.message import MessageEvent, error_message
from gamehub.core.request import (
    JoinGameByIdPayload,
    MakeMovePayload,
    Request,
    RequestType,
)


class RequestParser:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            MessageEvent(player_id=player_id, message=error_message(payload))
        )

    async def _parsed_payload(
        self, request: Request
    ) -> Optional[JoinGameByIdPayload | MakeMovePayload]:
        payload_cls = (
            JoinGameByIdPayload
            if request.request_type == RequestType.JOIN_GAME_BY_ID
            else MakeMovePayload
        )
        try:
            return payload_cls.model_validate(request.payload)
        except ValidationError as e:
            await self._respond_error(request.player_id, str(e))

    async def parse_request(self, request: Request) -> None:
        if payload := await self._parsed_payload(request):
            if isinstance(payload, JoinGameByIdPayload):
                new_event = JoinGameById(request.player_id, payload.room_id)
                await self._event_bus.publish(new_event)
            elif isinstance(payload, MakeMovePayload):
                new_event = MakeMove(request.player_id, payload.room_id, payload.move)
                await self._event_bus.publish(new_event)
