from typing import Optional

from pydantic import BaseModel, ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById, JoinGameByType, RejoinGame
from gamehub.core.events.make_move import MakeMove
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request import Request, RequestType
from gamehub.core.message import error_message


class _BasicRequestPayload(BaseModel):
    request_type: RequestType
    payload: dict


class RequestParser:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=error_message(payload))
        )

    async def pre_parse(self, request: Request) -> Optional[_BasicRequestPayload]:
        try:
            return _BasicRequestPayload.parse_raw(request.raw_request)
        except ValidationError as e:
            await self._respond_error(request.player_id, str(e))

    async def parse_request(self, request: Request) -> None:
        if pre_parsed := await self.pre_parse(request):
            payload = pre_parsed.payload
            payload["player_id"] = request.player_id
            event_cls = {
                RequestType.JOIN_GAME_BY_ID: JoinGameById,
                RequestType.JOIN_GAME_BY_TYPE: JoinGameByType,
                RequestType.REJOIN_GAME: RejoinGame,
                RequestType.MAKE_MOVE: MakeMove,
            }
            event = event_cls[pre_parsed.request_type].model_validate(payload)
            await self._event_bus.publish(event)
