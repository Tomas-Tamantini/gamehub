from collections import defaultdict
from enum import Enum
from typing import Optional

from gamehub.games.playing_cards import PlayingCard, Suits


def _rank_value(rank: chr) -> int:
    special_ranks = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14, "2": 15}
    return special_ranks[rank] if rank in special_ranks else int(rank)


def _suit_value(suit: Suits) -> int:
    return [Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES, Suits.CLUBS].index(suit)


def card_value(card: PlayingCard) -> int:
    return 4 * _rank_value(card.rank) + _suit_value(card.suit)


class _HandType(int, Enum):
    STRAIGHT = 1
    FLUSH = 2
    FULL_HOUSE = 3
    FOUR_OF_A_KIND = 4
    STRAIGHT_FLUSH = 5


def _last_card_in_straight(cards: set[PlayingCard]) -> Optional[PlayingCard]:
    sorted_cards = sorted(cards, key=lambda card: _rank_value(card.rank))
    ranks = tuple(card.rank for card in sorted_cards)
    if _rank_value(ranks[-1]) - _rank_value(ranks[0]) == 4:
        if ranks[-1] != "2":
            return sorted_cards[-1]
    elif ranks == ("3", "4", "5", "6", "2"):
        return sorted_cards[3]
    elif ranks == ("3", "4", "5", "A", "2"):
        return sorted_cards[2]


def _pair_and_three_of_a_kind_hand_value(cards: set[PlayingCard]) -> int:
    num_ranks = len({card.rank for card in cards})
    if num_ranks == 1:
        return max(card_value(card) for card in cards)
    else:
        raise ValueError("Invalid hand")


def _full_house_and_four_hand_value(rank_count: dict[int, int]) -> tuple[int, ...]:
    dominant_rank = max(rank_count, key=rank_count.get)
    if rank_count[dominant_rank] == 4:
        return _HandType.FOUR_OF_A_KIND, _rank_value(dominant_rank)
    else:
        return _HandType.FULL_HOUSE, _rank_value(dominant_rank)


def _straight_and_flush_hand_value(cards: set[PlayingCard]) -> tuple[int, ...]:
    is_flush = len({card.suit for card in cards}) == 1
    if last_card_in_straight := _last_card_in_straight(cards):
        if is_flush:
            return _HandType.STRAIGHT_FLUSH, card_value(last_card_in_straight)
        else:
            return _HandType.STRAIGHT, card_value(last_card_in_straight)
    elif is_flush:
        sorted_rank_values = sorted(
            (_rank_value(card.rank) for card in cards), reverse=True
        )
        return (
            _HandType.FLUSH,
            sorted_rank_values,
            _suit_value(next(iter(cards)).suit),
        )
    else:
        raise ValueError("Invalid hand")


def _five_card_hand_value(cards: set[PlayingCard]) -> tuple[int, ...]:
    rank_count = defaultdict(int)
    for card in cards:
        rank_count[card.rank] += 1

    if len(rank_count) == 2:
        return _full_house_and_four_hand_value(rank_count)
    elif len(rank_count) == 5:
        return _straight_and_flush_hand_value(cards)
    else:
        raise ValueError("Invalid hand")


def hand_value(hand: tuple[PlayingCard, ...]) -> tuple[int, ...]:
    cards = set(hand)
    if len(cards) == 1:
        return (card_value(next(iter(cards))),)
    elif 2 <= len(cards) <= 3:
        return (_pair_and_three_of_a_kind_hand_value(cards),)
    elif len(cards) == 5:
        return _five_card_hand_value(cards)
    else:
        raise ValueError("Invalid hand")
