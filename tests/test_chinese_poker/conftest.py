import pytest

from gamehub.games.chinese_poker import (
    ChinesePokerConfiguration,
    ChinesePokerGameLogic,
    ChinesePokerMove,
)
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.player import ChinesePokerPlayer
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.playing_cards import PlayingCard


def _parse_hand(cards: str) -> tuple[PlayingCard, ...]:
    return tuple(PlayingCard(rank=card[0], suit=card[1]) for card in cards.split())


@pytest.fixture
def initial_cards():
    hands_str = {
        "Alice": "3s 4h 5d 5h 6s 7d 9d 9c Qh Qs Kd Kh Kc",
        "Bob": "5c 6c 7c 8c 9h Td Th Tc Jc Qc Ks Ad 2d",
        "Charlie": "3h 3c 4d 4s 8d 9s Ts Jh Js Qd As Ac 2h",
        "Diana": "3d 4c 5s 6d 6h 7h 7s 8h 8s Jd Ah 2s 2c",
    }
    return {player_id: _parse_hand(hand) for player_id, hand in hands_str.items()}


@pytest.fixture
def moves_first_match():
    return [
        ChinesePokerMove(player_id="Diana", cards=_parse_hand("3d 4c 5s 6d 7h")),
        ChinesePokerMove(player_id="Alice", cards=_parse_hand("9d 9c Kd Kh Kc")),
        ChinesePokerMove(player_id="Bob", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Charlie", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Diana", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Alice", cards=_parse_hand("3s 4h 5d 6s 7d")),
        ChinesePokerMove(player_id="Bob", cards=_parse_hand("5c 6c 7c 8c Jc")),
        ChinesePokerMove(player_id="Charlie", cards=_parse_hand("4s 9s Ts Js As")),
        ChinesePokerMove(player_id="Dean", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Alice", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Bob", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Charlie", cards=_parse_hand("3h 3c")),
        ChinesePokerMove(player_id="Dean", cards=_parse_hand("8h 8s")),
        ChinesePokerMove(player_id="Alice", cards=_parse_hand("Qh Qs")),
        ChinesePokerMove(player_id="Bob", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Charlie", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Dean", cards=_parse_hand("")),
        ChinesePokerMove(player_id="Alice", cards=_parse_hand("5h")),
        ChinesePokerMove(player_id="Bob", cards=_parse_hand("2d")),
        ChinesePokerMove(player_id="Charlie", cards=_parse_hand("2h")),
        ChinesePokerMove(player_id="Dean", cards=_parse_hand("2c")),
    ]


@pytest.fixture
def moves_first_round(moves_first_match):
    return moves_first_match[:5]


@pytest.fixture
def first_move(moves_first_round):
    return moves_first_round[0]


def _make_moves(state, moves, game_logic):
    current_state = state
    for move in moves:
        while current_state.status != ChinesePokerStatus.AWAIT_PLAYER_ACTION:
            current_state = game_logic.next_automated_state(current_state)
        current_state = game_logic.make_move(current_state, move)
    return current_state


@pytest.fixture
def default_config():
    return ChinesePokerConfiguration(
        num_players=4, cards_per_player=13, game_over_point_threshold=25
    )


@pytest.fixture
def player_ids(initial_cards):
    return sorted(initial_cards.keys())


@pytest.fixture
def game_logic(default_config):
    return ChinesePokerGameLogic(default_config)


@pytest.fixture
def start_game(game_logic, player_ids):
    return game_logic.initial_state(*player_ids)


@pytest.fixture
def start_match(game_logic, start_game):
    return game_logic.next_automated_state(start_game)


@pytest.fixture
def deal_cards(player_ids, initial_cards):
    return ChinesePokerState(
        status=ChinesePokerStatus.DEAL_CARDS,
        players=[
            ChinesePokerPlayer(
                player_id=player_id, num_points=0, cards=initial_cards[player_id]
            )
            for player_id in player_ids
        ],
    )


@pytest.fixture
def start_round(game_logic, deal_cards):
    return game_logic.next_automated_state(deal_cards)


@pytest.fixture
def start_turn(game_logic, start_round):
    return game_logic.next_automated_state(start_round)


@pytest.fixture
def await_action(game_logic, start_turn):
    return game_logic.next_automated_state(start_turn)


@pytest.fixture
def end_turn(game_logic, await_action, first_move):
    return game_logic.make_move(await_action, first_move)


@pytest.fixture
def end_last_turn(game_logic, await_action, moves_first_round):
    return _make_moves(await_action, moves_first_round, game_logic)


@pytest.fixture
def end_round(game_logic, end_last_turn):
    return game_logic.next_automated_state(end_last_turn)


@pytest.fixture
def end_last_turn_of_match(game_logic, await_action, moves_first_match):
    return _make_moves(await_action, moves_first_match, game_logic)


@pytest.fixture
def end_last_round(game_logic, end_last_turn_of_match):
    return game_logic.next_automated_state(end_last_turn_of_match)


@pytest.fixture
def end_match(game_logic, end_last_round):
    return game_logic.next_automated_state(end_last_round)


@pytest.fixture
def update_points(game_logic, end_match):
    return game_logic.next_automated_state(end_match)


@pytest.fixture
def last_points_update(player_ids):
    points = [11, 13, 25, 17]
    return ChinesePokerState(
        status=ChinesePokerStatus.UPDATE_POINTS,
        players=[
            ChinesePokerPlayer(player_id=player_id, num_points=num_points, cards=())
            for player_id, num_points in zip(player_ids, points)
        ],
    )
