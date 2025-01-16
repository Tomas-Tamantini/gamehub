from typing import Generic, Protocol, TypeVar

from gamehub.core.game_state import GameState

T = TypeVar("T")


class GameLogic(Protocol, Generic[T]):
    @property
    def num_players(self) -> int: ...

    def initial_state(self, *player_ids: str) -> GameState: ...

    def make_move(self, state: GameState, move: T) -> GameState: ...
