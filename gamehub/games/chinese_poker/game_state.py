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
from gamehub.games.playing_cards import PlayingCard


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

    def next_player_has_zero_cards(self) -> bool:
        return len(self.players[self.next_player_idx()].cards) == 0

    def some_player_has_zero_cards(self) -> bool:
        return any(len(player.cards) == 0 for player in self.players)

    def idx_of_player_with_smallest_card(self) -> int:
        return min(
            range(len(self.players)),
            key=lambda idx: card_value(self.players[idx].smallest_card()),
        )

    def current_player(self) -> Optional[ChinesePokerPlayer]:
        if self.current_player_idx >= 0:
            return self.players[self.current_player_idx]

    def current_player_id(self) -> Optional[str]:
        if current_player := self.current_player():
            return current_player.player_id

    def shared_view(self) -> ChinesePokerSharedView:
        return ChinesePokerSharedView(
            status=self.status,
            players=map(lambda player: player.shared_view(), self.players),
            current_player_id=self.current_player_id(),
            move_history=self.move_history,
        )

    def max_points(self) -> int:
        return max(player.num_points for player in self.players)

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
        return self.status == ChinesePokerStatus.END_GAME

    def is_first_turn_of_match(self, num_cards_per_player) -> bool:
        return all(len(player.cards) == num_cards_per_player for player in self.players)

    def smallest_card(self) -> PlayingCard:
        return min((player.smallest_card() for player in self.players), key=card_value)

    def hand_to_beat(self) -> Optional[ChinesePokerMove]:
        for move in reversed(self.move_history):
            if not move.is_pass:
                return move
