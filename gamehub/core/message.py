from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    ERROR = "ERROR"
    GAME_ROOM_UPDATE = "GAME_ROOM_UPDATE"
    GAME_STATE = "GAME_STATE"
    TURN_TIMER_ALERT = "TURN_TIMER_ALERT"


class Message(BaseModel):
    message_type: MessageType
    payload: dict


def error_message(payload: str) -> Message:
    return Message(message_type=MessageType.ERROR, payload={"error": payload})
