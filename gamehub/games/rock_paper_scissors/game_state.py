from dataclasses import dataclass
from typing import Iterator

from gamehub.games.rock_paper_scissors.player import RPSPlayer
from gamehub.games.rock_paper_scissors.views import RPSPrivateView, RPSSharedView


@dataclass(frozen=True)
class RPSGameState:
    players: list[RPSPlayer]

    @property
    def _is_over(self) -> bool:
        return all(p.selection is not None for p in self.players)

    def shared_view(self) -> RPSSharedView:
        return RPSSharedView(players=[player.shared_view() for player in self.players])

    def private_views(self) -> Iterator[tuple[str, RPSPrivateView]]:
        if not self._is_over:
            for player in self.players:
                if player.selection is not None:
                    yield player.player_id, RPSPrivateView(selection=player.selection)
