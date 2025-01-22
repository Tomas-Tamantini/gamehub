from dataclasses import dataclass
from typing import Iterator, Optional

from gamehub.games.chinese_poker.card_value import card_value
from gamehub.games.chinese_poker.move import ChinesePokerMove
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
    move_history: tuple[ChinesePokerMove, ...] = ()

    def next_player_idx(self) -> int:
        if self.current_player_idx < 0:
            return -1
        else:
            return (self.current_player_idx + 1) % len(self.players)

    def last_players_passed(self) -> bool:
        num_passes_to_check = len(self.players) - 1
        return all(move.is_pass for move in self.move_history[-num_passes_to_check:])

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
            move_history=self.move_history,
        )

    def _players_to_send_private_view(self) -> Iterator[ChinesePokerPlayer]:
        if self.status == ChinesePokerStatus.DEAL_CARDS:
            yield from self.players
        elif self.status in {
            ChinesePokerStatus.AWAIT_PLAYER_ACTION,
            ChinesePokerStatus.END_TURN,
        }:
            yield self.players[self.current_player_idx]

    def private_views(self):
        for player in self._players_to_send_private_view():
            yield player.player_id, ChinesePokerPrivateView(
                status=self.status, cards=player.cards
            )

    def is_terminal(self) -> bool:
        # TODO: Implement
        return False
