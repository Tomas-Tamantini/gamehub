from typing import Iterable, Iterator, Optional

from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.player import player_initial_state
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.chinese_poker.transitions import (
    next_automated_state,
    state_after_move,
)
from gamehub.games.playing_cards import PlayingCard


class ChinesePokerGameLogic:
    def __init__(self, configuration: ChinesePokerConfiguration):
        self._configuration = configuration

    @property
    def game_type(self) -> str:
        return "chinese_poker"

    @property
    def configuration(self) -> ChinesePokerConfiguration:
        return self._configuration

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
        return state_after_move(state, move, self._configuration)

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        return next_automated_state(state, self._configuration)

    @staticmethod
    def derived_events(
        state: ChinesePokerState, room_id: int, recipients: Iterable[str]
    ) -> Iterator[object]:
        if state.status == ChinesePokerStatus.START_GAME:
            yield GameStarted(room_id=room_id)
        elif state.status == ChinesePokerStatus.END_GAME:
            yield GameEnded(room_id=room_id)
        elif state.status == ChinesePokerStatus.AWAIT_PLAYER_ACTION:
            yield TurnStarted(
                room_id=room_id,
                player_id=state.current_player_id(),
                recipients=recipients,
            )
        elif state.status == ChinesePokerStatus.END_TURN:
            yield TurnEnded(room_id=room_id, player_id=state.current_player_id())

    @staticmethod
    def _automatic_move_cards(state: ChinesePokerState) -> tuple[PlayingCard]:
        if state.move_history:
            return tuple()
        else:
            return (state.current_player().smallest_card(),)

    def state_after_timeout(
        self, state: ChinesePokerState, timed_out_player_id: str
    ) -> Optional[ChinesePokerState]:
        if (state.status == ChinesePokerStatus.AWAIT_PLAYER_ACTION) and (
            state.current_player_id() == timed_out_player_id
        ):
            cards = self._automatic_move_cards(state)
            move = ChinesePokerMove(player_id=timed_out_player_id, cards=cards)
            return self.make_move(state, move)
