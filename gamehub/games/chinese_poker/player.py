from dataclasses import dataclass

from gamehub.games.chinese_poker.views import ChinesePokerPlayerSharedView


@dataclass(frozen=True)
class ChinesePokerPlayer:
    player_id: str
    num_points: int
    cards: tuple

    def shared_view(self) -> ChinesePokerPlayerSharedView:
        return ChinesePokerPlayerSharedView(
            player_id=self.player_id,
            num_points=self.num_points,
            num_cards=len(self.cards),
        )


def player_initial_state(player_id: str) -> ChinesePokerPlayer:
    return ChinesePokerPlayer(player_id=player_id, num_points=0, cards=tuple())
