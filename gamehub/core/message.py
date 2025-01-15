from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    ERROR = "ERROR"


class Message(BaseModel):
    message_type: MessageType
    payload: str


@dataclass(frozen=True)
class MessageEvent:
    player_id: str
    message: Message
