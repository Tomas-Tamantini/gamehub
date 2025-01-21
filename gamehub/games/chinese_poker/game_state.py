from dataclasses import dataclass

from gamehub.games.chinese_poker.player import ChinesePokerPlayer
from gamehub.games.chinese_poker.views import (
    ChinesePokerSharedView,
)


@dataclass(frozen=True)
class ChinesePokerState:
    players: tuple[ChinesePokerPlayer, ...]

    def shared_view(self) -> ChinesePokerSharedView:
        return ChinesePokerSharedView(
            players=map(lambda player: player.shared_view(), self.players)
        )
