from typing import Generic, Optional, Protocol, TypeVar

from gamehub.core.game_state import GameState

MoveType = TypeVar("MoveType")
GameConfigType = TypeVar("GameConfigType")


class GameLogic(Protocol, Generic[MoveType, GameConfigType]):
    @property
    def num_players(self) -> int: ...

    @property
    def game_type(self) -> str: ...

    @property
    def configuration(self) -> Optional[GameConfigType]: ...

    def initial_state(self, *player_ids: str) -> GameState: ...

    def make_move(self, state: GameState, move: MoveType) -> GameState: ...

    def next_automated_state(self, state: GameState) -> Optional[GameState]: ...
