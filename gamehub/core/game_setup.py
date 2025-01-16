from dataclasses import dataclass
from typing import Callable

from gamehub.core.game_state import GameState


@dataclass(frozen=True)
class GameSetup:
    num_players: int
    initial_state: Callable[[list[str]], GameState]
