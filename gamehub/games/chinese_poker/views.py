from typing import Optional

from pydantic import BaseModel

from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.playing_cards import PlayingCard


class ChinesePokerPlayerSharedView(BaseModel):
    player_id: str
    num_points: int
    num_cards: int


class ChinesePokerPlayerResult(BaseModel):
    player_id: str
    dist_to_avg: float


class ChinesePokerResult(BaseModel):
    players: tuple[ChinesePokerPlayerResult, ...]


class ChinesePokerSharedView(BaseModel):
    status: ChinesePokerStatus
    players: tuple[ChinesePokerPlayerSharedView, ...]
    current_player_id: Optional[str]
    move_history: tuple[ChinesePokerMove, ...]
    result: Optional[ChinesePokerResult]


class ChinesePokerPrivateView(BaseModel):
    status: ChinesePokerStatus
    cards: tuple[PlayingCard, ...]
