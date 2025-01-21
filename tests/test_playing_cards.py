import pytest
from pydantic import ValidationError

from gamehub.games.playing_cards import PlayingCard, Suits, deal_hands


@pytest.mark.parametrize("invalid_rank", ["x", "0", "1", "t", "k"])
def test_card_rank_must_be_valid_character(invalid_rank):
    with pytest.raises(ValidationError):
        PlayingCard(rank=invalid_rank, suit=Suits.SPADES)


def test_cannot_deal_more_than_52_cards():
    with pytest.raises(ValueError, match="more than 52"):
        next(deal_hands(num_hands=3, hand_size=18))


def test_cards_are_dealt_without_repetition():
    unique_cards = set()
    for hand in deal_hands(num_hands=13, hand_size=4):
        unique_cards.update(set(hand))
    assert len(unique_cards) == 52
