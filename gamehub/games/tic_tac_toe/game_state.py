from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


class TicTacToeState:
    def __init__(self, players: tuple[TicTacToePlayer, TicTacToePlayer]):
        self._players = players

    def shared_view(self) -> TicTacToeView:
        return TicTacToeView(players=self._players)

    @staticmethod
    def private_views():
        yield from []

    def is_terminal(self) -> bool:
        raise NotImplementedError()
