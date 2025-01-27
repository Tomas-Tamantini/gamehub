
from gamehub.games.playing_cards import PlayingCard, Suits


def rank_value(rank: chr) -> int:
    special_ranks = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14, "2": 15}
    return special_ranks[rank] if rank in special_ranks else int(rank)


def suit_value(suit: Suits) -> int:
    return [Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES, Suits.CLUBS].index(suit)


def card_value(card: PlayingCard) -> int:
    return 4 * rank_value(card.rank) + suit_value(card.suit)
