from typing import Generic, Optional, TypeVar

from pydantic import ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.exceptions import InvalidMoveError
from gamehub.core.game_logic import GameLogic
from gamehub.core.game_state import GameState
from gamehub.core.message import Message, MessageType
from gamehub.core.move_parser import MoveParser
from gamehub.core.room_state import RoomState

MoveType = TypeVar("MoveType")
GameConfigType = TypeVar("GameConfigType")


class GameRoom(Generic[MoveType, GameConfigType]):
    def __init__(
        self,
        room_id: int,
        game_logic: GameLogic[MoveType, GameConfigType],
        move_parser: MoveParser[MoveType],
        event_bus: EventBus,
    ):
        self._room_id = room_id
        self._logic = game_logic
        self._event_bus = event_bus
        self._players = list()
        self._spectators = set()
        self._offline_players = set()
        self._game_state = None
        self._parse_move = move_parser

    @property
    def game_type(self) -> str:
        return self._logic.game_type

    @property
    def is_full(self) -> bool:
        return len(self._players) >= self._logic.num_players

    def _reset(self) -> None:
        self._players = list()
        self._spectators = set()
        self._offline_players = set()
        self._game_state = None

    async def _set_game_state(self, state: GameState) -> None:
        self._game_state = state
        await self._send_private_views()
        await self._broadcast_shared_view()
        if state.is_terminal():
            self._reset()
        elif new_state := self._logic.next_automated_state(state):
            await self._set_game_state(new_state)

    @property
    def room_id(self) -> int:
        return self._room_id

    def room_state(self) -> RoomState[GameConfigType]:
        return RoomState[GameConfigType](
            room_id=self._room_id,
            capacity=self._logic.num_players,
            player_ids=self._players[:],
            offline_players=list(self._offline_players),
            is_full=self.is_full,
            configuration=self._logic.configuration,
        )

    async def _send_message(self, player_id: str, message: Message) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=message)
        )

    async def _broadcast_message(self, message: Message) -> None:
        for player in self._players:
            await self._send_message(player, message)
        for spectator in self._spectators:
            await self._send_message(spectator, message)

    def _room_state_message(self) -> Message:
        return Message(
            message_type=MessageType.GAME_ROOM_UPDATE,
            payload=self.room_state().model_dump(),
        )

    async def _broadcast_room_state(self) -> None:
        await self._broadcast_message(self._room_state_message())

    def _shared_view_payload(self) -> dict:
        shared_view = self._game_state.shared_view(self._logic.configuration)
        return {
            "room_id": self._room_id,
            "shared_view": shared_view.model_dump(exclude_none=True),
        }

    def _shared_view_message(self) -> Message:
        return Message(
            message_type=MessageType.GAME_STATE, payload=self._shared_view_payload()
        )

    async def _broadcast_shared_view(self) -> None:
        await self._broadcast_message(self._shared_view_message())

    async def _send_private_views(self) -> None:
        for player_id, private_view in self._game_state.private_views():
            message = Message(
                message_type=MessageType.GAME_STATE,
                payload={
                    "room_id": self._room_id,
                    "private_view": private_view.model_dump(exclude_none=True),
                },
            )
            await self._event_bus.publish(
                OutgoingMessage(player_id=player_id, message=message)
            )

    async def _start_game(self) -> None:
        await self._set_game_state(self._logic.initial_state(*self._players))

    def _add_player(self, player_id: str) -> None:
        self._players.append(player_id)
        if player_id in self._spectators:
            self._spectators.remove(player_id)

    async def join(self, player_id: str) -> None:
        if player_id in self._players:
            await self._event_bus.publish(
                RequestFailed(player_id, "Player already in room")
            )
        elif self.is_full:
            await self._event_bus.publish(
                RequestFailed(player_id, "Unable to join: Room is full")
            )
        else:
            self._add_player(player_id)
            await self._broadcast_room_state()
            if self.is_full:
                await self._start_game()

    async def rejoin(self, player_id: str) -> None:
        if player_id not in self._players:
            await self._event_bus.publish(
                RequestFailed(player_id, "Player not in room")
            )
        elif player_id not in self._offline_players:
            await self._event_bus.publish(
                RequestFailed(player_id, "Player is not offline")
            )
        else:
            self._offline_players.remove(player_id)
            await self._broadcast_room_state()
            await self._send_full_game_state(player_id)

    async def add_spectator(self, player_id: str) -> None:
        if player_id in self._players:
            await self._event_bus.publish(
                RequestFailed(
                    player_id, "Already joined game. Cannot watch as spectator"
                )
            )
        else:
            self._spectators.add(player_id)
            await self._send_message(player_id, self._room_state_message())
            if self._game_state:
                await self._send_message(player_id, self._shared_view_message())

    async def _send_full_game_state(self, player_id: str) -> None:
        if self._game_state is not None:
            payload = self._shared_view_payload()
            if private_view := self._game_state.query_private_view(player_id):
                payload["private_view"] = private_view.model_dump(exclude_none=True)
            message = Message(message_type=MessageType.GAME_STATE, payload=payload)
            await self._event_bus.publish(
                OutgoingMessage(player_id=player_id, message=message)
            )

    async def _parsed_move(self, player_id: str, raw_move: dict) -> Optional[MoveType]:
        try:
            return self._parse_move({"player_id": player_id, **raw_move})
        except ValidationError as e:
            await self._event_bus.publish(RequestFailed(player_id, str(e)))

    async def _game_state_after_move(
        self, player_id: str, parsed_move: MoveType
    ) -> Optional[GameState]:
        try:
            return self._logic.make_move(self._game_state, parsed_move)
        except InvalidMoveError as e:
            await self._event_bus.publish(RequestFailed(player_id, str(e)))

    async def make_move(self, player_id: str, move: dict) -> None:
        if player_id not in self._players:
            await self._event_bus.publish(
                RequestFailed(player_id, "Player not in room")
            )
        elif not self._game_state:
            await self._event_bus.publish(
                RequestFailed(player_id, "Game has not started yet")
            )
        elif parsed_move := await self._parsed_move(player_id, move):
            if new_state := await self._game_state_after_move(player_id, parsed_move):
                await self._set_game_state(new_state)

    async def handle_player_disconnected(self, player_id: str) -> None:
        if player_id in self._players:
            if self._game_state is None:
                self._players.remove(player_id)
            else:
                self._offline_players.add(player_id)
            await self._broadcast_room_state()
        elif player_id in self._spectators:
            self._spectators.remove(player_id)
