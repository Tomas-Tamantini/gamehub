from typing import Optional

from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove


class ChinesePokerGameLogic:
    @property
    def game_type(self) -> str:
        return "chinese_poker"

    @property
    def num_players(self) -> int:
        raise NotImplementedError()

    def initial_state(self, *player_ids: str) -> ChinesePokerState:
        raise NotImplementedError()

    def make_move(
        self, state: ChinesePokerState, move: ChinesePokerMove
    ) -> ChinesePokerState:
        raise NotImplementedError()

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        raise NotImplementedError()
