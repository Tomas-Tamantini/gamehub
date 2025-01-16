import json
from typing import Generic, TypeVar

from gamehub.core.event_bus import EventBus
from gamehub.core.game_logic import GameLogic
from gamehub.core.message import Message, MessageEvent, MessageType
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
        self._game_state = None
        self._parse_move = move_parser

    @property
    def _is_full(self) -> bool:
        return len(self._players) >= self._logic.num_players

    @property
    def room_id(self) -> int:
        return self._room_id

    def _room_state(self) -> str:
        return json.dumps({"room_id": self._room_id, "player_ids": self._players})

    async def _send_error_message(self, player_id: str, payload: str) -> None:
        await self._event_bus.publish(
            MessageEvent(
                player_id=player_id,
                message=Message(message_type=MessageType.ERROR, payload=payload),
            )
        )

    async def _broadcast_message(self, message: Message) -> None:
        for player in self._players:
            await self._event_bus.publish(
                MessageEvent(player_id=player, message=message)
            )

    async def _broadcast_shared_view(self) -> None:
        message_payload = {
            "room_id": self._room_id,
            "shared_view": self._game_state.shared_view().model_dump(),
        }
        message = Message(
            message_type=MessageType.GAME_STATE, payload=json.dumps(message_payload)
        )
        await self._broadcast_message(message)

    async def _send_private_views(self) -> None:
        for player_id, private_view in self._game_state.private_views():
            message_payload = {
                "room_id": self._room_id,
                "private_view": private_view.model_dump(),
            }
            message = Message(
                message_type=MessageType.GAME_STATE, payload=json.dumps(message_payload)
            )
            await self._event_bus.publish(
                MessageEvent(player_id=player_id, message=message)
            )

    async def _start_game(self) -> None:
        self._game_state = self._logic.initial_state(*self._players)
        await self._broadcast_shared_view()

    async def join(self, player_id: str) -> None:
        if player_id in self._players:
            await self._send_error_message(
                player_id=player_id, payload="Player already in room"
            )
        elif self._is_full:
            await self._send_error_message(
                player_id=player_id, payload="Unable to join: Room is full"
            )
        else:
            self._players.append(player_id)
            message = Message(
                message_type=MessageType.PLAYER_JOINED, payload=self._room_state()
            )
            await self._broadcast_message(message)
            if self._is_full:
                await self._start_game()

    async def make_move(self, player_id: str, move: dict) -> None:
        parsed_move = self._parse_move({"player_id": player_id, **move})
        new_state = self._logic.make_move(self._game_state, parsed_move)
        self._game_state = new_state
        await self._send_private_views()
        await self._broadcast_shared_view()
