from typing import Protocol

from gamehub.core.message import MessageEvent


class MessageSender(Protocol):
    async def send(self, message: MessageEvent) -> None: ...
