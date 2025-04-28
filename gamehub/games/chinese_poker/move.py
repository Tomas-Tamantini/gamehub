from pydantic import BaseModel

from gamehub.games.playing_cards import PlayingCard


class ChinesePokerMove(BaseModel):
    player_id: str
    cards: tuple[PlayingCard, ...]
    is_bot_move: bool = False

    @property
    def is_pass(self) -> bool:
        return not self.cards
