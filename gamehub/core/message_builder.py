from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_room_update import GameRoomUpdate
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.message import Message, MessageType, error_message


class MessageBuilder:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    async def build_error_message(self, failed_request: RequestFailed) -> None:
        await self._event_bus.publish(
            OutgoingMessage(
                player_id=failed_request.player_id,
                message=error_message(failed_request.error_msg),
            )
        )

    async def notify_room_update(self, room_update: GameRoomUpdate) -> None:
        msg = Message(
            message_type=MessageType.GAME_ROOM_UPDATE,
            payload=room_update.room_state.model_dump(),
        )
        for player in room_update.room_state.player_ids:
            await self._event_bus.publish(
                OutgoingMessage(player_id=player, message=msg)
            )
        for spectator in room_update.spectators:
            await self._event_bus.publish(
                OutgoingMessage(player_id=spectator, message=msg)
            )
