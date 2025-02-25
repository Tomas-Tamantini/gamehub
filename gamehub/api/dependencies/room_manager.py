from functools import lru_cache
from typing import Annotated, Iterator

from fastapi import Depends

from gamehub.api.dependencies.event_bus import T_EventBus
from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.room_manager import RoomManager
from gamehub.games.chinese_poker import (
    ChinesePokerConfiguration,
    ChinesePokerGameLogic,
    ChinesePokerMove,
)
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove


# TODO: Extract room factories to Game module
def _tic_tac_toe_room(event_bus: EventBus, room_id: int) -> GameRoom:
    return GameRoom(
        room_id=room_id,
        game_logic=TicTacToeGameLogic(),
        move_parser=TicTacToeMove.model_validate,
        event_bus=event_bus,
    )


def _rps_room(event_bus: EventBus, room_id: int) -> GameRoom:
    return GameRoom(
        room_id=room_id,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )


def _chinese_poker_configuration() -> ChinesePokerConfiguration:
    return ChinesePokerConfiguration(
        num_players=4, cards_per_player=13, game_over_point_threshold=25
    )


def _chinese_poker_room(event_bus: EventBus, room_id: int) -> GameRoom:
    return GameRoom(
        room_id=room_id,
        game_logic=ChinesePokerGameLogic(_chinese_poker_configuration()),
        move_parser=ChinesePokerMove.model_validate,
        event_bus=event_bus,
    )


def _default_rooms(event_bus: EventBus) -> Iterator[GameRoom]:
    yield _chinese_poker_room(event_bus, room_id=1)
    yield _chinese_poker_room(event_bus, room_id=2)
    yield _rps_room(event_bus, room_id=3)
    yield _tic_tac_toe_room(event_bus, room_id=4)


@lru_cache
def get_room_manager(event_bus: T_EventBus) -> RoomManager:
    return RoomManager(
        rooms=list(_default_rooms(event_bus)),
        event_bus=event_bus,
    )


T_RoomManager = Annotated[RoomManager, Depends(get_room_manager)]
