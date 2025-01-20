from pydantic import BaseModel


class TicTacToePlayer(BaseModel):
    player_id: str
    selections: set[int] = set()

    def select(self, cell_index: int) -> "TicTacToePlayer":
        new_selections = self.selections | {cell_index}
        return TicTacToePlayer(player_id=self.player_id, selections=new_selections)
