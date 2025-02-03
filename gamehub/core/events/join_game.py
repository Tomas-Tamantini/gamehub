from dataclasses import dataclass


@dataclass(frozen=True)
class JoinGameById:
    player_id: str
    room_id: int


@dataclass(frozen=True)
class RejoinGame:
    player_id: str
    room_id: int


@dataclass(frozen=True)
class JoinGameByType:
    player_id: str
    game_type: str
