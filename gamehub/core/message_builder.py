from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request_events import RequestFailed
from gamehub.core.message import error_message


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
