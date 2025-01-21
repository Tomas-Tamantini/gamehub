from typing import Optional

from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.player import ChinesePokerPlayer


class ChinesePokerGameLogic:
    def __init__(self, configuration: ChinesePokerConfiguration):
        self._configuration = configuration

    @property
    def game_type(self) -> str:
        return "chinese_poker"

    @property
    def num_players(self) -> int:
        return self._configuration.num_players

    @staticmethod
    def initial_state(*player_ids: str) -> ChinesePokerState:
        return ChinesePokerState(
            players=tuple(
                ChinesePokerPlayer(player_id, num_points=0) for player_id in player_ids
            )
        )

    def make_move(
        self, state: ChinesePokerState, move: ChinesePokerMove
    ) -> ChinesePokerState:
        raise NotImplementedError()

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        raise NotImplementedError()
