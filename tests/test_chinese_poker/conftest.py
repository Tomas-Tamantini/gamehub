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
def first_move():
    return ChinesePokerMove()


@pytest.fixture
def default_config():
    return ChinesePokerConfiguration(num_players=4, cards_per_player=13)


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
