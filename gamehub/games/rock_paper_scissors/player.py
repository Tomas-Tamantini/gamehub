from dataclasses import dataclass
from typing import Optional

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.rock_paper_scissors.selection import RPSSelection
from gamehub.games.rock_paper_scissors.views import RPSSharedPlayerView


@dataclass(frozen=True)
class RPSPlayer:
    player_id: str
    selection: Optional[RPSSelection]

    def make_selection(self, selection: RPSSelection) -> "RPSPlayer":
        if self.selection is not None:
            raise InvalidMoveError(f"{self.player_id} has already selected")
        else:
            return RPSPlayer(player_id=self.player_id, selection=selection)

    def shared_view(self) -> RPSSharedPlayerView:
        return RPSSharedPlayerView(
            player_id=self.player_id,
            selected=self.selection is not None,
        )
