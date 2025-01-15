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

    @property
    def room_id(self) -> int:
        return self._room_id

    def _state(self) -> str:
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

    async def join(self, player_id: str) -> None:
        if player_id in self._players:
            await self._send_error_message(
                player_id=player_id, payload="Player already in room"
            )
        elif len(self._players) >= self._setup.num_players:
            await self._send_error_message(
                player_id=player_id, payload="Unable to join: Room is full"
            )
        else:
            self._players.append(player_id)
            message = Message(
                message_type=MessageType.PLAYER_JOINED, payload=self._state()
            )
            await self._broadcast_message(message)
