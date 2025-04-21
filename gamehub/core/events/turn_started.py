from dataclasses import dataclass


@dataclass(frozen=True)
class TurnStarted:
    room_id: int
    player_id: str
