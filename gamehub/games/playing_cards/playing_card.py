from typing import Literal

from pydantic import BaseModel

from gamehub.games.playing_cards.suits import Suits


class PlayingCard(BaseModel):
    rank: Literal["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    suit: Suits

    class Config:
        frozen = True
