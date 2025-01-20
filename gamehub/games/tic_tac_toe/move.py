from pydantic import BaseModel, Field


class TicTacToeMove(BaseModel):
    player_id: str
    cell_index: int = Field(..., ge=0, le=8)
