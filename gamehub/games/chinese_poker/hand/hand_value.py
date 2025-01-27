from collections import defaultdict
from typing import Optional

from gamehub.games.chinese_poker.hand.card_value import (
    card_value,
    rank_value,
    suit_value,
)
from gamehub.games.chinese_poker.hand.hand_type import HandType
from gamehub.games.playing_cards import PlayingCard


def _last_card_in_straight(cards: set[PlayingCard]) -> Optional[PlayingCard]:
    sorted_cards = sorted(cards, key=lambda card: rank_value(card.rank))
    ranks = tuple(card.rank for card in sorted_cards)
    if rank_value(ranks[-1]) - rank_value(ranks[0]) == 4:
        if ranks[-1] != "2":
            return sorted_cards[-1]
    elif ranks == ("3", "4", "5", "6", "2"):
        return sorted_cards[3]
    elif ranks == ("3", "4", "5", "A", "2"):
        return sorted_cards[2]


def _high_card_to_three_of_a_kink_value(cards: set[PlayingCard]) -> int:
    num_ranks = len({card.rank for card in cards})
    if num_ranks == 1:
        return max(card_value(card) for card in cards)
    else:
        raise ValueError("Invalid hand")


def _full_house_and_four_hand_value(rank_count: dict[int, int]) -> tuple[int, ...]:
    dominant_rank = max(rank_count, key=rank_count.get)
    if rank_count[dominant_rank] == 4:
        return HandType.FOUR_OF_A_KIND, rank_value(dominant_rank)
    else:
        return HandType.FULL_HOUSE, rank_value(dominant_rank)


def _straight_and_flush_hand_value(cards: set[PlayingCard]) -> tuple[int, ...]:
    is_flush = len({card.suit for card in cards}) == 1
    if last_card_in_straight := _last_card_in_straight(cards):
        if is_flush:
            return HandType.STRAIGHT_FLUSH, card_value(last_card_in_straight)
        else:
            return HandType.STRAIGHT, card_value(last_card_in_straight)
    elif is_flush:
        sorted_rank_values = sorted(
            (rank_value(card.rank) for card in cards), reverse=True
        )
        return (
            HandType.FLUSH,
            sorted_rank_values,
            suit_value(next(iter(cards)).suit),
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
    if 1 <= len(cards) <= 3:
        return (_high_card_to_three_of_a_kink_value(cards),)
    elif len(cards) == 5:
        return _five_card_hand_value(cards)
    else:
        raise ValueError("Invalid hand")
