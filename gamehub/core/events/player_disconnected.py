from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerDisconnected:
    player_id: str
