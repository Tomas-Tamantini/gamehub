from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TurnTimerAlert:
    room_id: int
    player_id: str
    seconds_remaining: int
    recipients: Iterable[str]


@dataclass(frozen=True)
class TurnTimeout:
    room_id: int
    player_id: str
    recipients: Iterable[str]
