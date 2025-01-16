from dataclasses import dataclass
from typing import Iterator, Optional

from gamehub.games.rock_paper_scissors.player import RPSPlayer
from gamehub.games.rock_paper_scissors.selection import RPSSelection
from gamehub.games.rock_paper_scissors.views import (
    RPSPlayerView,
    RPSPrivateView,
    RPSResultView,
    RPSSharedView,
)


@dataclass(frozen=True)
class RPSGameState:
    players: list[RPSPlayer]

    @property
    def _is_over(self) -> bool:
        return all(p.selection is not None for p in self.players)

    @staticmethod
    def _beats(selection_a: RPSSelection, selection_b: RPSSelection) -> bool:
        cyclic = [RPSSelection.ROCK, RPSSelection.PAPER, RPSSelection.SCISSORS]
        idx_a = cyclic.index(selection_a)
        idx_b = cyclic.index(selection_b)
        return (idx_a - idx_b) % 3 == 1

    def _winner(self) -> Optional[str]:
        selections = [p.selection for p in self.players]
        if selections[0] == selections[1]:
            return None
        else:
            return (
                self.players[0].player_id
                if self._beats(selections[0], selections[1])
                else self.players[1].player_id
            )

    def _result(self) -> Optional[RPSResultView]:
        if not self._is_over:
            return None
        moves = [
            RPSPlayerView(player_id=player.player_id, selection=player.selection)
            for player in self.players
        ]
        return RPSResultView(winner=self._winner(), moves=moves)

    def shared_view(self) -> RPSSharedView:
        return RPSSharedView(
            players=[player.shared_view() for player in self.players],
            result=self._result(),
        )

    def private_views(self) -> Iterator[tuple[str, RPSPrivateView]]:
        if not self._is_over:
            for player in self.players:
                if player.selection is not None:
                    yield player.player_id, RPSPrivateView(selection=player.selection)
