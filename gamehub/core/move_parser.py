from typing import Callable, TypeVar

T = TypeVar("T")
MoveParser = Callable[[dict], T]
