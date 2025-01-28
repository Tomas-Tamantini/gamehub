from dataclasses import dataclass

from gamehub.core.message import Message


@dataclass(frozen=True)
class OutgoingMessage:
    player_id: str
    message: Message
