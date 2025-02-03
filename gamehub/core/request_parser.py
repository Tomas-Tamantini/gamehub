from pydantic import ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById, JoinGameByType, RejoinGame
from gamehub.core.events.make_move import MakeMove
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.query_rooms import QueryRooms
from gamehub.core.events.request import (
    JoinGameByIdPayload,
    JoinGameByTypePayload,
    MakeMovePayload,
    QueryRoomsPayload,
    RejoinGamePayload,
    Request,
    RequestType,
)
from gamehub.core.message import error_message


class _JoinByIdParser:
    @property
    def model(self):
        return JoinGameByIdPayload

    @staticmethod
    def create_new_event(
        player_id: str, parsed_payload: JoinGameByIdPayload
    ) -> JoinGameById:
        return JoinGameById(player_id, parsed_payload.room_id)


class _JoinByTypeParser:
    @property
    def model(self):
        return JoinGameByTypePayload

    @staticmethod
    def create_new_event(
        player_id: str, parsed_payload: JoinGameByTypePayload
    ) -> JoinGameByType:
        return JoinGameByType(player_id, parsed_payload.game_type)


class _RejoinGameParser:
    @property
    def model(self):
        return RejoinGamePayload

    @staticmethod
    def create_new_event(
        player_id: str, parsed_payload: RejoinGamePayload
    ) -> RejoinGame:
        return RejoinGame(player_id, parsed_payload.room_id)


class _MakeMoveParser:
    @property
    def model(self):
        return MakeMovePayload

    @staticmethod
    def create_new_event(
        player_id: str, parsed_payload: MakeMovePayload
    ) -> MakeMovePayload:
        return MakeMove(player_id, parsed_payload.room_id, parsed_payload.move)


class _QueryRoomParser:
    @property
    def model(self):
        return QueryRoomsPayload

    @staticmethod
    def create_new_event(
        player_id: str, parsed_payload: QueryRoomsPayload
    ) -> QueryRooms:
        return QueryRooms(player_id, parsed_payload.game_type)


class RequestParser:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=error_message(payload))
        )

    async def parse_request(self, request: Request) -> None:
        parser = {
            RequestType.JOIN_GAME_BY_ID: _JoinByIdParser,
            RequestType.JOIN_GAME_BY_TYPE: _JoinByTypeParser,
            RequestType.MAKE_MOVE: _MakeMoveParser,
            RequestType.QUERY_ROOMS: _QueryRoomParser,
            RequestType.REJOIN_GAME: _RejoinGameParser,
        }[request.request_type]()
        try:
            payload = parser.model.model_validate(request.payload)
            new_event = parser.create_new_event(request.player_id, payload)
            await self._event_bus.publish(new_event)
        except ValidationError as e:
            await self._respond_error(request.player_id, str(e))
