from dataclasses import dataclass
from typing import Iterable

from pydantic import BaseModel


@dataclass(frozen=True)
class GameStateUpdate:
    room_id: int
    shared_view: BaseModel
    private_views: dict[str, BaseModel]
    recipients: Iterable[str]


@dataclass(frozen=True)
class TurnStarted:
    room_id: int
    player_id: str


@dataclass(frozen=True)
class TurnEnded:
    room_id: int
    player_id: str
