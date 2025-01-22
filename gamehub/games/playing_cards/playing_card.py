from typing import Literal

from pydantic import BaseModel, ConfigDict

from gamehub.games.playing_cards.suits import Suits


class PlayingCard(BaseModel):
    model_config: ConfigDict = {"frozen": True}

    rank: Literal["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    suit: Suits
