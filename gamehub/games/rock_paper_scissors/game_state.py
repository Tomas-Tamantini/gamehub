from dataclasses import dataclass

from gamehub.games.rock_paper_scissors.player import RPSPlayer
from gamehub.games.rock_paper_scissors.shared_view import RPSSharedView


@dataclass(frozen=True)
class RPSGameState:
    players: list[RPSPlayer]

    def shared_view(self) -> RPSSharedView:
        return RPSSharedView(players=[player.shared_view() for player in self.players])
