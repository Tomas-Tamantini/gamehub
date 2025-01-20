from dataclasses import dataclass

# TODO: Bring other event classes to this folder


@dataclass(frozen=True)
class JoinGameById:
    player_id: str
    room_id: int
