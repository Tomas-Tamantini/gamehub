from dataclasses import dataclass

from gamehub.games.chinese_poker.card_value import card_value
from gamehub.games.chinese_poker.views import ChinesePokerPlayerSharedView
from gamehub.games.playing_cards import PlayingCard


@dataclass(frozen=True)
class ChinesePokerPlayer:
    player_id: str
    num_points: int
    cards: tuple[PlayingCard, ...]

    def shared_view(self) -> ChinesePokerPlayerSharedView:
        return ChinesePokerPlayerSharedView(
            player_id=self.player_id,
            num_points=self.num_points,
            num_cards=len(self.cards),
        )

    def deal_cards(self, cards: tuple[PlayingCard, ...]) -> "ChinesePokerPlayer":
        return ChinesePokerPlayer(
            player_id=self.player_id,
            num_points=self.num_points,
            cards=cards,
        )

    def remove_cards(self, cards: tuple[PlayingCard, ...]) -> "ChinesePokerPlayer":
        return ChinesePokerPlayer(
            player_id=self.player_id,
            num_points=self.num_points,
            cards=tuple(card for card in self.cards if card not in cards),
        )

    def increment_points(self) -> "ChinesePokerPlayer":
        return ChinesePokerPlayer(
            player_id=self.player_id,
            num_points=self.num_points + len(self.cards),
            cards=tuple(),
        )

    def smallest_card(self) -> PlayingCard:
        return min(self.cards, key=card_value)

    def has_cards(self, cards: tuple[PlayingCard, ...]) -> bool:
        return all(card in self.cards for card in cards)


def player_initial_state(player_id: str) -> ChinesePokerPlayer:
    return ChinesePokerPlayer(player_id=player_id, num_points=0, cards=tuple())
