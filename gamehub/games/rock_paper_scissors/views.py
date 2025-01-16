from pydantic import BaseModel


class RPSSharedPlayerView(BaseModel):
    player_id: str
    selected: bool


class RPSSharedView(BaseModel):
    players: list[RPSSharedPlayerView]


class RPSPrivateView(BaseModel):
    selection: str
