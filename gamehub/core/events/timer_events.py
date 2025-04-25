from dataclasses import dataclass


@dataclass(frozen=True)
class TurnTimerAlert:
    room_id: int
    player_id: str
    time_left_seconds: int
