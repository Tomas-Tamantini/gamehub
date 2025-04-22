from dataclasses import dataclass


@dataclass(frozen=True)
class TurnEnded:
    room_id: int
    player_id: str
