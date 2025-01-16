from pydantic import BaseModel

from gamehub.games.rock_paper_scissors.selection import RPSSelection


class RPSMove(BaseModel):
    player_id: str
    selection: RPSSelection
