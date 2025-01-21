from dataclasses import dataclass


@dataclass(frozen=True)
class ChinesePokerConfiguration:
    num_players: int
