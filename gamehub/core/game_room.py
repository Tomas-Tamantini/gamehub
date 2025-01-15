from gamehub.core.event_bus import EventBus
from gamehub.core.message import Message, MessageEvent, MessageType
import json


class GameRoom:
    def __init__(self, room_id: int, event_bus: EventBus):
        self._room_id = room_id
        self._event_bus = event_bus
        self._players = []

    @property
    def room_id(self) -> int:
        return self._room_id

    def _state(self) -> str:
        return json.dumps({"room_id": self._room_id, "player_ids": self._players})

    async def _broadcast_message(self, message: Message) -> None:
        for player in self._players:
            await self._event_bus.publish(
                MessageEvent(player_id=player, message=message)
            )

    async def join(self, player_id: str) -> None:
        self._players.append(player_id)
        message = Message(message_type=MessageType.PLAYER_JOINED, payload=self._state())
        await self._broadcast_message(message)
