from typing import Optional

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.player import player_initial_state
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.playing_cards import deal_hands


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

    @staticmethod
    def _players_after_move(state: ChinesePokerState, move: ChinesePokerMove):
        for player in state.players:
            if player.player_id == move.player_id:
                yield player.remove_cards(move.cards)
            else:
                yield player

    @staticmethod
    def make_move(
        state: ChinesePokerState, move: ChinesePokerMove
    ) -> ChinesePokerState:
        if state.status != ChinesePokerStatus.AWAIT_PLAYER_ACTION:
            raise InvalidMoveError("Cannot make move at this time")
        else:
            return ChinesePokerState(
                status=ChinesePokerStatus.END_TURN,
                players=tuple(ChinesePokerGameLogic._players_after_move(state, move)),
                current_player_idx=state.current_player_idx,
                move_history=state.move_history + (move,),
            )

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        if state.status == ChinesePokerStatus.START_GAME:
            return ChinesePokerState(
                status=ChinesePokerStatus.START_MATCH,
                players=state.players,
            )
        elif state.status == ChinesePokerStatus.START_MATCH:
            hands = deal_hands(
                num_hands=self.num_players,
                hand_size=self._configuration.cards_per_player,
            )
            return ChinesePokerState(
                status=ChinesePokerStatus.DEAL_CARDS,
                players=[p.deal_cards(hand) for p, hand in zip(state.players, hands)],
            )
        elif state.status == ChinesePokerStatus.DEAL_CARDS:
            return ChinesePokerState(
                status=ChinesePokerStatus.START_ROUND,
                players=state.players,
                current_player_idx=state.idx_of_player_with_smallest_card(),
            )
        elif state.status == ChinesePokerStatus.START_ROUND:
            return ChinesePokerState(
                status=ChinesePokerStatus.START_TURN,
                players=state.players,
                current_player_idx=state.current_player_idx,
            )
        elif state.status == ChinesePokerStatus.START_TURN:
            return ChinesePokerState(
                status=ChinesePokerStatus.AWAIT_PLAYER_ACTION,
                players=state.players,
                current_player_idx=state.current_player_idx,
                move_history=state.move_history,
            )
        elif state.status == ChinesePokerStatus.END_TURN:
            if state.last_players_passed() or state.next_player_has_zero_cards():
                return ChinesePokerState(
                    status=ChinesePokerStatus.END_ROUND,
                    players=state.players,
                    current_player_idx=state.next_player_idx(),
                    move_history=state.move_history,
                )
            else:
                return ChinesePokerState(
                    status=ChinesePokerStatus.START_TURN,
                    players=state.players,
                    current_player_idx=state.next_player_idx(),
                    move_history=state.move_history,
                )
        elif state.status == ChinesePokerStatus.END_ROUND:
            if state.some_player_has_zero_cards():
                return ChinesePokerState(
                    status=ChinesePokerStatus.END_MATCH,
                    players=state.players,
                )
            else:
                return ChinesePokerState(
                    status=ChinesePokerStatus.START_ROUND,
                    players=state.players,
                    current_player_idx=state.current_player_idx,
                )
