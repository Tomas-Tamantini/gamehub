from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


class TicTacToeState:
    def __init__(self, players: tuple[TicTacToePlayer, TicTacToePlayer]):
        self._players = players

    @property
    def players(self) -> tuple[TicTacToePlayer, TicTacToePlayer]:
        return self._players

    def shared_view(self) -> TicTacToeView:
        return TicTacToeView(players=self._players)

    @staticmethod
    def private_views():
        yield from []

    def is_terminal(self) -> bool:
        raise NotImplementedError()

    @property
    def _current_turn_idx(self) -> int:
        if len(self._players[0].selections) == len(self._players[1].selections):
            return 0
        else:
            return 1

    def current_turn(self) -> str:
        return self._players[self._current_turn_idx].player_id

    def selected_cells(self) -> set[int]:
        return self._players[0].selections | self._players[1].selections
