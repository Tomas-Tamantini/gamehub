from typing import Iterator

from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


class TicTacToeState:
    def __init__(self, players: tuple[TicTacToePlayer, TicTacToePlayer]):
        self._players = players

    @property
    def players(self) -> tuple[TicTacToePlayer, TicTacToePlayer]:
        return self._players

    def shared_view(self) -> TicTacToeView:
        return TicTacToeView(
            players=self._players, is_over=self.is_terminal(), winner=self._winner()
        )

    @staticmethod
    def private_views():
        yield from []

    def is_terminal(self) -> bool:
        return len(self.selected_cells()) == 9 or self._winner() is not None

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

    @staticmethod
    def _winning_combinations() -> Iterator[set[int]]:
        yield from (
            {0, 1, 2},
            {3, 4, 5},
            {6, 7, 8},
            {0, 3, 6},
            {1, 4, 7},
            {2, 5, 8},
            {0, 4, 8},
            {2, 4, 6},
        )

    def _winner(self) -> str:
        for player in self._players:
            for win_set in TicTacToeState._winning_combinations():
                if win_set.issubset(player.selections):
                    return player.player_id
        return None
