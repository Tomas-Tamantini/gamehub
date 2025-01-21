from dataclasses import dataclass

from gamehub.games.chinese_poker.views import ChinesePokerPlayerSharedView


@dataclass(frozen=True)
class ChinesePokerPlayer:
    player_id: str
    num_points: int

    def shared_view(self) -> ChinesePokerPlayerSharedView:
        return ChinesePokerPlayerSharedView(
            player_id=self.player_id, num_points=self.num_points
        )
