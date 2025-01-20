from gamehub.games.tic_tac_toe.game_state import TicTacToeState
from gamehub.games.tic_tac_toe.move import TicTacToeMove
from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.core.exceptions import InvalidMoveError


class TicTacToeGameLogic:
    @property
    def num_players(self) -> int:
        return 2

    @staticmethod
    def initial_state(*player_ids: str) -> TicTacToeState:
        return TicTacToeState(
            players=(
                TicTacToePlayer(player_id=player_id, selections=set())
                for player_id in player_ids
            )
        )

    def make_move(self, state: TicTacToeState, move: TicTacToeMove) -> TicTacToeState:
        raise InvalidMoveError("Not player's turn")
