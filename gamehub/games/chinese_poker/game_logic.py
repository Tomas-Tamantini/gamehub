from typing import Optional

from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.player import player_initial_state
from gamehub.games.chinese_poker.status import ChinesePokerStatus


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
            status=ChinesePokerStatus.START_GAME,
            players=tuple(player_initial_state(player_id) for player_id in player_ids),
        )

    def make_move(
        self, state: ChinesePokerState, move: ChinesePokerMove
    ) -> ChinesePokerState:
        raise NotImplementedError()

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        if state.status == ChinesePokerStatus.START_GAME:
            return ChinesePokerState(
                status=ChinesePokerStatus.START_MATCH,
                players=state.players,
            )
        elif state.status == ChinesePokerStatus.START_MATCH:
            return ChinesePokerState(
                status=ChinesePokerStatus.DEAL_CARDS,
                players=state.players,
            )
