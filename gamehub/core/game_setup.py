from dataclasses import dataclass


@dataclass(frozen=True)
class GameSetup:
    num_players: int
