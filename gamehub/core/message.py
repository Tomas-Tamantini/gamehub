from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    ERROR = "ERROR"
    PLAYER_JOINED = "PLAYER_JOINED"
    PLAYER_DISCONNECTED = "PLAYER_DISCONNECTED"
    GAME_STATE = "GAME_STATE"


class Message(BaseModel):
    message_type: MessageType
    payload: dict


def error_message(payload: str) -> Message:
    return Message(message_type=MessageType.ERROR, payload={"error": payload})
