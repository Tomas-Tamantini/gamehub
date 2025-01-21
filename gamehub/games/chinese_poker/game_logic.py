from typing import Optional

from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove


class ChinesePokerGameLogic:
    def __init__(self, configuration: ChinesePokerConfiguration):
        self._configuration = configuration

    @property
    def game_type(self) -> str:
        return "chinese_poker"

    @property
    def num_players(self) -> int:
        return self._configuration.num_players

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
