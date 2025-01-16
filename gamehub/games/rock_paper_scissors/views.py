from typing import Optional

from pydantic import BaseModel

from gamehub.games.rock_paper_scissors.selection import RPSSelection


class RPSPrivateView(BaseModel):
    selection: RPSSelection


class RPSPlayerView(RPSPrivateView):
    player_id: str


class RPSResultView(BaseModel):
    winner: Optional[str]
    moves: list[RPSPlayerView]


class RPSSharedPlayerView(BaseModel):
    player_id: str
    selected: bool


class RPSSharedView(BaseModel):
    players: list[RPSSharedPlayerView]
    result: Optional[RPSResultView] = None
