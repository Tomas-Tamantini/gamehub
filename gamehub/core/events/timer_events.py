from dataclasses import dataclass


@dataclass(frozen=True)
class TurnTimerAlert:
    room_id: int
    player_id: str
    seconds_remaining: int


@dataclass(frozen=True)
class TurnTimeout:
    room_id: int
    player_id: str
