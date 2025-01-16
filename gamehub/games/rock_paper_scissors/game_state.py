from dataclasses import dataclass
from typing import Optional

from gamehub.games.rock_paper_scissors.selection import RPSSelection
from gamehub.games.rock_paper_scissors.shared_view import (
    RPSSharedPlayerView,
    RPSSharedView,
)


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
