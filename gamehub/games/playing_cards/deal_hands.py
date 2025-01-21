from random import shuffle
from typing import Iterator

from gamehub.games.playing_cards.playing_card import PlayingCard
from gamehub.games.playing_cards.suits import Suits


def deal_hands(num_hands: int, hand_size: int) -> Iterator[tuple[PlayingCard, ...]]:
    if num_hands * hand_size > 52:
        raise ValueError("Cannot deal more than 52 cards")
    ranks = "23456789TJQKA"
    deck = [PlayingCard(rank=rank, suit=suit) for rank in ranks for suit in Suits]
    shuffle(deck)
    for i in range(num_hands):
        yield tuple(deck[i * hand_size : (i + 1) * hand_size])
