from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.tic_tac_toe.game_state import TicTacToeState
from gamehub.games.tic_tac_toe.move import TicTacToeMove
from gamehub.games.tic_tac_toe.player import TicTacToePlayer


class TicTacToeGameLogic:
    @property
    def num_players(self) -> int:
        return 2

    @property
    def game_type(self) -> str:
        return "tic_tac_toe"

    @staticmethod
    def initial_state(*player_ids: str) -> TicTacToeState:
        return TicTacToeState(
            players=tuple(
                TicTacToePlayer(player_id=player_id, selections=set())
                for player_id in player_ids
            )
        )

    @staticmethod
    def make_move(state: TicTacToeState, move: TicTacToeMove) -> TicTacToeState:
        if state.is_terminal():
            raise InvalidMoveError("Game is over")
        if move.player_id != state.current_turn():
            raise InvalidMoveError("Not player's turn")
        if move.cell_index in state.selected_cells():
            raise InvalidMoveError("Cell already selected")
        new_players = []
        for p in state.players:
            new_player = (
                p if p.player_id != state.current_turn() else p.select(move.cell_index)
            )
            new_players.append(new_player)
        return TicTacToeState(players=tuple(new_players))
