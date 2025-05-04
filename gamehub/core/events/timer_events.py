from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class TurnTimerAlert:
    room_id: int
    player_id: str
    turn_expires_at: datetime
    recipients: Iterable[str]


@dataclass(frozen=True)
class TurnTimeout:
    room_id: int
    player_id: str
    recipients: Iterable[str]
