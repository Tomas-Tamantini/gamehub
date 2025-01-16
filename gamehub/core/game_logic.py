from typing import Protocol

from gamehub.core.game_state import GameState


class GameLogic(Protocol):
    @property
    def num_players(self) -> int: ...

    def initial_state(self, *player_ids: str) -> GameState: ...
