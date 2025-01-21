from pydantic import BaseModel

from gamehub.games.chinese_poker.status import ChinesePokerStatus


class ChinesePokerPlayerSharedView(BaseModel):
    player_id: str
    num_points: int
    num_cards: int


class ChinesePokerSharedView(BaseModel):
    status: ChinesePokerStatus
    players: tuple[ChinesePokerPlayerSharedView, ...]
