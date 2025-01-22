from pydantic import BaseModel

from gamehub.games.playing_cards import PlayingCard


class ChinesePokerMove(BaseModel):
    player_id: str
    cards: tuple[PlayingCard, ...]
