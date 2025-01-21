from pydantic import BaseModel


class ChinesePokerPlayerSharedView(BaseModel):
    player_id: str
    num_points: int
    num_cards: int


class ChinesePokerSharedView(BaseModel):
    players: tuple[ChinesePokerPlayerSharedView, ...]
