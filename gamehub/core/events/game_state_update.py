from dataclasses import dataclass
from typing import Iterable

from pydantic import BaseModel


@dataclass(frozen=True)
class GameStateUpdate:
    room_id: int
    shared_view: BaseModel
    private_views: dict[str, BaseModel]
    recipients: Iterable[str]
