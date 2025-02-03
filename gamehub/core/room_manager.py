from typing import Iterator

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById, JoinGameByType, RejoinGame
from gamehub.core.events.make_move import MakeMove
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.query_rooms import QueryRooms
from gamehub.core.game_room import GameRoom
from gamehub.core.message import Message, MessageType, error_message


class RoomManager:
    def __init__(self, rooms: list[GameRoom], event_bus: EventBus):
        self._rooms = {room.room_id: room for room in rooms}
        self._event_bus = event_bus

    async def _respond_error(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=error_message(payload))
        )

    async def join_game_by_id(self, join_game: JoinGameById) -> None:
        if not (room := self._rooms.get(join_game.room_id)):
            await self._respond_error(
                join_game.player_id, f"Room with id {join_game.room_id} does not exist"
            )
        else:
            await room.join(join_game.player_id)

    async def rejoin_game(self, join_game: RejoinGame) -> None:
        if not (room := self._rooms.get(join_game.room_id)):
            await self._respond_error(
                join_game.player_id, f"Room with id {join_game.room_id} does not exist"
            )
        else:
            await room.rejoin(join_game.player_id)

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

    async def query_rooms(self, query: QueryRooms) -> None:
        await self._event_bus.publish(
            OutgoingMessage(
                player_id=query.player_id,
                message=Message(
                    message_type=MessageType.GAME_ROOMS,
                    payload={
                        "rooms": [
                            r.room_state().model_dump()
                            for r in self._rooms_by_game_type(query.game_type)
                        ]
                    },
                ),
            )
        )
