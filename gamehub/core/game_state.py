from typing import Protocol


class _SharedView(Protocol):
    def model_dump(self) -> dict: ...


class GameState(Protocol):
    def shared_view(self) -> _SharedView: ...
