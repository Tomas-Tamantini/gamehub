from typing import Optional

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.hand import hand_value
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.player import player_initial_state
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.chinese_poker.transitions import next_automated_state


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

    def make_move(
        self, state: ChinesePokerState, move: ChinesePokerMove
    ) -> ChinesePokerState:
        if state.status != ChinesePokerStatus.AWAIT_PLAYER_ACTION:
            raise InvalidMoveError("Cannot make move at this time")
        current_player = state.current_player()
        if not current_player or current_player.player_id != move.player_id:
            raise InvalidMoveError("It is not your turn")
        elif not current_player.has_cards(move.cards):
            raise InvalidMoveError("You do not have those cards")
        elif move.is_pass and not state.move_history:
            raise InvalidMoveError("First player of the round cannot pass")
        elif (
            state.is_first_turn_of_match(self._configuration.cards_per_player)
            and state.smallest_card() not in move.cards
        ):
            raise InvalidMoveError("First player of the match must use smallest card")
        hand_to_beat = state.hand_to_beat()
        if (
            hand_to_beat
            and not move.is_pass
            and len(move.cards) != len(hand_to_beat.cards)
        ):
            raise InvalidMoveError(
                "Must use the same number of cards as the hand to beat"
            )
        if not move.is_pass:
            try:
                move_value = hand_value(move.cards)
            except ValueError as e:
                raise InvalidMoveError(str(e))

            if hand_to_beat and move_value <= hand_value(hand_to_beat.cards):
                raise InvalidMoveError("Hand does not beat previous hand")

        return ChinesePokerState(
            status=ChinesePokerStatus.END_TURN,
            players=tuple(ChinesePokerGameLogic._players_after_move(state, move)),
            current_player_idx=state.current_player_idx,
            move_history=state.move_history + (move,),
        )

    def next_automated_state(
        self, state: ChinesePokerState
    ) -> Optional[ChinesePokerState]:
        return next_automated_state(state, self._configuration)
