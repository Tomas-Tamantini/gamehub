from typing import Generic, Optional, TypeVar

from pydantic import ValidationError

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.exceptions import InvalidMoveError
from gamehub.core.game_logic import GameLogic
from gamehub.core.game_state import GameState
from gamehub.core.message import Message, MessageType, error_message
from gamehub.core.move_parser import MoveParser

T = TypeVar("T")


class GameRoom(Generic[T]):
    def __init__(
        self,
        room_id: int,
        game_logic: GameLogic[T],
        move_parser: MoveParser[T],
        event_bus: EventBus,
    ):
        self._room_id = room_id
        self._logic = game_logic
        self._event_bus = event_bus
        self._players = list()
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
        self._offline_players = set()
        self._game_state = None

    async def _set_state(self, state: GameState) -> None:
        self._game_state = state
        await self._send_private_views()
        await self._broadcast_shared_view()
        if state.is_terminal():
            self._reset()
        elif new_state := self._logic.next_automated_state(state):
            await self._set_state(new_state)

    @property
    def room_id(self) -> int:
        return self._room_id

    def _room_state(self) -> dict:
        return {
            "room_id": self._room_id,
            "player_ids": self._players[:],
            "offline_players": list(self._offline_players),
        }

    async def _send_error_message(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            OutgoingMessage(player_id=player_id, message=error_message(payload))
        )

    async def _broadcast_message(self, message: Message) -> None:
        for player in self._players:
            await self._event_bus.publish(
                OutgoingMessage(player_id=player, message=message)
            )

    async def _broadcast_shared_view(self) -> None:
        message = Message(
            message_type=MessageType.GAME_STATE,
            payload={
                "room_id": self._room_id,
                "shared_view": self._game_state.shared_view().model_dump(
                    exclude_none=True
                ),
            },
        )
        await self._broadcast_message(message)

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
        await self._set_state(self._logic.initial_state(*self._players))

    async def join(self, player_id: str) -> None:
        if player_id in self._players:
            await self._send_error_message(
                player_id=player_id, payload="Player already in room"
            )
        elif self.is_full:
            await self._send_error_message(
                player_id=player_id, payload="Unable to join: Room is full"
            )
        else:
            self._players.append(player_id)
            message = Message(
                message_type=MessageType.PLAYER_JOINED, payload=self._room_state()
            )
            await self._broadcast_message(message)
            if self.is_full:
                await self._start_game()

    async def _parsed_move(self, player_id: str, raw_move: dict) -> Optional[T]:
        try:
            return self._parse_move({"player_id": player_id, **raw_move})
        except ValidationError as e:
            await self._send_error_message(player_id=player_id, payload=str(e))

    async def _state_after_move(
        self, player_id: str, parsed_move: T
    ) -> Optional[GameState]:
        try:
            return self._logic.make_move(self._game_state, parsed_move)
        except InvalidMoveError as e:
            await self._send_error_message(player_id=player_id, payload=str(e))

    async def make_move(self, player_id: str, move: dict) -> None:
        if player_id not in self._players:
            await self._send_error_message(
                player_id=player_id, payload="Player not in room"
            )
        elif not self._game_state:
            await self._send_error_message(
                player_id=player_id, payload="Game has not started yet"
            )
        elif parsed_move := await self._parsed_move(player_id, move):
            if new_state := await self._state_after_move(player_id, parsed_move):
                await self._set_state(new_state)

    async def handle_player_disconnected(self, player_id: str) -> None:
        if player_id in self._players:
            if self._game_state is None:
                self._players.remove(player_id)
            else:
                self._offline_players.add(player_id)
            message = Message(
                message_type=MessageType.PLAYER_DISCONNECTED, payload=self._room_state()
            )
            await self._broadcast_message(message)
