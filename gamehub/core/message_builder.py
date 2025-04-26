from typing import Optional

from pydantic import BaseModel

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_room_update import GameRoomUpdate
from gamehub.core.events.game_state_update import GameStateUpdate
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.events.sync_client_state import SyncClientState
from gamehub.core.events.timer_events import TurnTimeout, TurnTimerAlert
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
        msg = self._room_state_message(room_update.room_state)
        for recipient in room_update.recipients:
            await self._event_bus.publish(
                OutgoingMessage(player_id=recipient, message=msg)
            )

    async def notify_game_state_update(self, game_update: GameStateUpdate) -> None:
        await self._notify_private_views(game_update)
        await self._broadcast_shared_view(game_update)

    async def sync_client_state(self, sync_state: SyncClientState) -> None:
        msg = self._room_state_message(sync_state.room_state)
        await self._event_bus.publish(
            OutgoingMessage(player_id=sync_state.client_id, message=msg)
        )
        game_state_msg = self._game_state_message(
            room_id=sync_state.room_state.room_id,
            shared_view=sync_state.shared_view,
            private_view=sync_state.private_view,
        )
        if len(game_state_msg.payload) > 1:
            await self._event_bus.publish(
                OutgoingMessage(player_id=sync_state.client_id, message=game_state_msg)
            )

    async def notify_turn_timer_alert(self, turn_timer_alert: TurnTimerAlert) -> None:
        msg = Message(
            message_type=MessageType.TURN_TIMER_ALERT,
            payload={
                "room_id": turn_timer_alert.room_id,
                "player_id": turn_timer_alert.player_id,
                "seconds_remaining": turn_timer_alert.seconds_remaining,
            },
        )
        for recipient in turn_timer_alert.recipients:
            await self._event_bus.publish(
                OutgoingMessage(player_id=recipient, message=msg)
            )

    async def notify_turn_timeout(self, turn_timeout: TurnTimeout) -> None:
        msg = Message(
            message_type=MessageType.TURN_TIMER_ALERT,
            payload={
                "room_id": turn_timeout.room_id,
                "player_id": turn_timeout.player_id,
                "seconds_remaining": 0,
            },
        )
        for recipient in turn_timeout.recipients:
            await self._event_bus.publish(
                OutgoingMessage(player_id=recipient, message=msg)
            )

    @staticmethod
    def _room_state_message(room_state: BaseModel) -> Message:
        return Message(
            message_type=MessageType.GAME_ROOM_UPDATE, payload=room_state.model_dump()
        )

    @staticmethod
    def _game_state_message(
        room_id: int,
        shared_view: Optional[BaseModel],
        private_view: Optional[BaseModel],
    ) -> Message:
        payload = {"room_id": room_id}
        if shared_view:
            payload["shared_view"] = shared_view.model_dump(exclude_none=True)
        if private_view:
            payload["private_view"] = private_view.model_dump(exclude_none=True)
        return Message(message_type=MessageType.GAME_STATE, payload=payload)

    async def _broadcast_shared_view(self, game_update):
        shared_view_msg = self._game_state_message(
            game_update.room_id, shared_view=game_update.shared_view, private_view=None
        )
        for recipient in game_update.recipients:
            await self._event_bus.publish(
                OutgoingMessage(player_id=recipient, message=shared_view_msg)
            )

    async def _notify_private_views(self, game_update):
        for player_id, private_view in game_update.private_views.items():
            private_view_msg = self._game_state_message(
                game_update.room_id, shared_view=None, private_view=private_view
            )
            await self._event_bus.publish(
                OutgoingMessage(player_id=player_id, message=private_view_msg)
            )
