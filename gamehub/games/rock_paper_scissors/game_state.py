from dataclasses import dataclass
from enum import Enum
from typing import Optional

from gamehub.games.rock_paper_scissors.shared_view import (
    RPSSharedPlayerView,
    RPSSharedView,
)


class RPSSelection(Enum):
    ROCK = "ROCK"
    PAPER = "PAPER"
    SCISSORS = "SCISSORS"


@dataclass(frozen=True)
class RPSPlayer:
    player_id: str
    selection: Optional[RPSSelection]

    def shared_view(self) -> RPSSharedPlayerView:
        return RPSSharedPlayerView(
            player_id=self.player_id,
            selected=self.selection is not None,
        )


@dataclass(frozen=True)
class RPSGameState:
    players: list[RPSPlayer]

    def shared_view(self) -> RPSSharedView:
        return RPSSharedView(players=[player.shared_view() for player in self.players])
