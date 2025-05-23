from typing import Generic, Iterator, Optional, Protocol, TypeVar

T = TypeVar("T")


class _View(Protocol):
    def model_dump(self, *_, exclude_none: bool) -> dict: ...


class GameState(Protocol, Generic[T]):
    def shared_view(self, configuration: T) -> _View: ...

    def private_views(self) -> Iterator[tuple[str, _View]]: ...

    def query_private_view(self, player_id: str) -> Optional[_View]: ...

    def is_terminal(self) -> bool: ...
