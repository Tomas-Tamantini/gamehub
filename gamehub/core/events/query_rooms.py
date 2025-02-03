from dataclasses import dataclass


@dataclass(frozen=True)
class QueryRooms:
    player_id: str
    game_type: str
