import json

from gamehub.core.event_bus import EventBus
from gamehub.core.game_setup import GameSetup
from gamehub.core.message import Message, MessageEvent, MessageType


class GameRoom:
    def __init__(self, room_id: int, setup: GameSetup, event_bus: EventBus):
        self._room_id = room_id
        self._setup = setup
        self._event_bus = event_bus
        self._players = list()
        self._game_state = None

    @property
    def _is_full(self) -> bool:
        return len(self._players) >= self._setup.num_players

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
            "shared_view": self._game_state.shared_view(),
        }
        message = Message(
            message_type=MessageType.GAME_STATE, payload=json.dumps(message_payload)
        )
        await self._broadcast_message(message)

    async def _start_game(self) -> None:
        self._game_state = self._setup.initial_state(self._players)
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
