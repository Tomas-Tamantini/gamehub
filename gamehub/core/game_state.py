from typing import Protocol


class GameState(Protocol):
    def shared_view(self) -> dict: ...
