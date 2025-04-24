from typing import Iterator

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.games.chinese_poker import (
    ChinesePokerConfiguration,
    ChinesePokerGameLogic,
    ChinesePokerMove,
)
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove


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


def _chinese_poker_room(
    event_bus: EventBus, room_id: int, point_threshold: int, credits_per_point: int
) -> GameRoom:
    return GameRoom(
        room_id=room_id,
        game_logic=ChinesePokerGameLogic(
            ChinesePokerConfiguration(
                num_players=4,
                cards_per_player=13,
                game_over_point_threshold=point_threshold,
                credits_per_point=credits_per_point,
            )
        ),
        move_parser=ChinesePokerMove.model_validate,
        event_bus=event_bus,
    )


def default_rooms(event_bus: EventBus) -> Iterator[GameRoom]:
    yield _chinese_poker_room(
        event_bus, room_id=1, point_threshold=25, credits_per_point=100
    )
    yield _chinese_poker_room(
        event_bus, room_id=2, point_threshold=25, credits_per_point=200
    )
    yield _chinese_poker_room(
        event_bus, room_id=3, point_threshold=20, credits_per_point=400
    )
    yield _rps_room(event_bus, room_id=4)
    yield _tic_tac_toe_room(event_bus, room_id=5)
