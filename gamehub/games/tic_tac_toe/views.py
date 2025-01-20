from typing import Optional

from pydantic import BaseModel

from gamehub.games.tic_tac_toe.player import TicTacToePlayer


class TicTacToeView(BaseModel):
    players: tuple[TicTacToePlayer, TicTacToePlayer]
    is_over: bool = False
    winner: Optional[str] = None
