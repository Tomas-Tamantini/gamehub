from typing import Generic, Iterable, Iterator, Optional, Protocol, TypeVar

from gamehub.core.game_state import GameState

S = TypeVar("S", bound=GameState)
M = TypeVar("M")
C = TypeVar("C")


class GameLogic(Protocol, Generic[S, M, C]):
    @property
    def num_players(self) -> int: ...

    @property
    def game_type(self) -> str: ...

    @property
    def configuration(self) -> Optional[C]: ...

    def initial_state(self, *player_ids: str) -> S: ...

    def make_move(self, state: S, move: M) -> S: ...

    def next_automated_state(self, state: S) -> Optional[S]: ...

    def derived_events(
        self, state: S, room_id: int, recipients: Iterable[str]
    ) -> Iterator[object]: ...

    def state_after_timeout(
        self, state: S, timed_out_player_id: str
    ) -> Optional[S]: ...
