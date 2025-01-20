from pydantic import BaseModel


class TicTacToePlayer(BaseModel):
    player_id: str
    selections: set[int] = set()
