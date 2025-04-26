from dataclasses import dataclass
from typing import Iterable

from pydantic import BaseModel


@dataclass(frozen=True)
class _GameStateEvent:
    room_id: int


@dataclass(frozen=True)
class GameStateUpdate(_GameStateEvent):
    shared_view: BaseModel
    private_views: dict[str, BaseModel]
    recipients: Iterable[str]


@dataclass(frozen=True)
class GameStarted(_GameStateEvent): ...


@dataclass(frozen=True)
class GameEnded(_GameStateEvent): ...


@dataclass(frozen=True)
class TurnStarted(_GameStateEvent):
    player_id: str
    recipients: Iterable[str]


@dataclass(frozen=True)
class TurnEnded(_GameStateEvent):
    player_id: str
