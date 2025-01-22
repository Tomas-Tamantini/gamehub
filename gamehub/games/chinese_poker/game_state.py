from dataclasses import dataclass
from typing import Optional

from gamehub.games.chinese_poker.card_value import card_value
from gamehub.games.chinese_poker.player import ChinesePokerPlayer
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.chinese_poker.views import (
    ChinesePokerPrivateView,
    ChinesePokerSharedView,
)


@dataclass(frozen=True)
class ChinesePokerState:
    status: ChinesePokerStatus
    players: tuple[ChinesePokerPlayer, ...]
    current_player_idx: int = -1

    def idx_of_player_with_smallest_card(self) -> int:
        return min(
            range(len(self.players)),
            key=lambda idx: min(card_value(card) for card in self.players[idx].cards),
        )

    def current_player_id(self) -> Optional[str]:
        if self.current_player_idx >= 0:
            return self.players[self.current_player_idx].player_id

    def shared_view(self) -> ChinesePokerSharedView:
        return ChinesePokerSharedView(
            status=self.status,
            players=map(lambda player: player.shared_view(), self.players),
            current_player_id=self.current_player_id(),
        )

    def private_views(self):
        if self.status == ChinesePokerStatus.DEAL_CARDS:
            for player in self.players:
                yield player.player_id, ChinesePokerPrivateView(
                    status=self.status, cards=player.cards
                )

    def is_terminal(self) -> bool:
        # TODO: Implement
        return False
