from typing import Awaitable, Callable, Iterator, Optional

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request_events import (
    DirectedRequest,
    JoinGameById,
    JoinGameByType,
    MakeMove,
    RejoinGame,
    WatchGame,
)
from gamehub.core.game_room import GameRoom
from gamehub.core.message import error_message
from gamehub.core.room_state import RoomState


class RoomManager:
    def __init__(self, rooms: list[GameRoom], event_bus: EventBus):
        self._rooms = {room.room_id: room for room in rooms}
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=error_message(payload))
        )

    async def _handle_directed_request(
        self,
        request: DirectedRequest,
        handler: Callable[[GameRoom, str], Awaitable[None]],
    ) -> None:
        if not (room := self._rooms.get(request.room_id)):
            await self._respond_error(
                request.player_id, f"Room with id {request.room_id} does not exist"
            )
        else:
            await handler(room, request.player_id)

    async def join_game_by_id(self, request: JoinGameById) -> None:
        async def handler(room, player_id):
            await room.join(player_id)

        await self._handle_directed_request(request, handler)

    async def rejoin_game(self, request: RejoinGame) -> None:
        async def handler(room, player_id):
            await room.rejoin(player_id)

        await self._handle_directed_request(request, handler)

    async def watch_game(self, request: WatchGame) -> None:
        async def handler(room, player_id):
            await room.add_spectator(player_id)

        await self._handle_directed_request(request, handler)

    def _rooms_by_game_type(self, game_type: str) -> Iterator[GameRoom]:
        for room in self._rooms.values():
            if room.game_type == game_type:
                yield room

    async def join_game_by_type(self, join_game: JoinGameByType) -> None:
        for room in self._rooms_by_game_type(join_game.game_type):
            if not room.is_full:
                await room.join(join_game.player_id)
                return

        await self._respond_error(
            join_game.player_id,
            f"No available room for game type {join_game.game_type}",
        )

    async def make_move(self, make_move: MakeMove) -> None:
        if not (room := self._rooms.get(make_move.room_id)):
            await self._respond_error(
                make_move.player_id, f"Room with id {make_move.room_id} does not exist"
            )
        else:
            await room.make_move(make_move.player_id, make_move.move)

    async def handle_player_disconnected(
        self, player_disconnected: PlayerDisconnected
    ) -> None:
        for room in self._rooms.values():
            await room.handle_player_disconnected(player_disconnected.player_id)

    def room_states(self, game_type: Optional[str] = None) -> Iterator[RoomState]:
        if game_type is None:
            for room in self._rooms.values():
                yield room.room_state()
        else:
            for room in self._rooms_by_game_type(game_type):
                yield room.room_state()
