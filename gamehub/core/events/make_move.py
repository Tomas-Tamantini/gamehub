from dataclasses import dataclass


@dataclass(frozen=True)
class MakeMove:
    player_id: str
    room_id: int
    move: dict
