from typing import Protocol

from gamehub.core.events.outgoing_message import OutgoingMessage


class MessageSender(Protocol):
    async def send(self, message: OutgoingMessage) -> None: ...
