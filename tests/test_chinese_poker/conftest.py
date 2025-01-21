import pytest

from gamehub.games.chinese_poker import ChinesePokerConfiguration, ChinesePokerGameLogic


@pytest.fixture
def default_config():
    return ChinesePokerConfiguration(num_players=4, cards_per_player=13)


@pytest.fixture
def player_ids():
    return "Alice", "Bob", "Charlie", "Diana"


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
def deal_cards(game_logic, start_match):
    return game_logic.next_automated_state(start_match)
