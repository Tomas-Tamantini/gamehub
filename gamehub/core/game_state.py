from typing import Iterator, Protocol


class _View(Protocol):
    def model_dump(self, *_, exclude_none: bool) -> dict: ...


class GameState(Protocol):
    def shared_view(self) -> _View: ...

    def private_views(self) -> Iterator[tuple[str, _View]]: ...

    def is_terminal(self) -> bool: ...
