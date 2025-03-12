from dataclasses import dataclass


@dataclass(frozen=True)
class ChinesePokerConfiguration:
    num_players: int
    cards_per_player: int
    game_over_point_threshold: int
    credits_per_point: int
