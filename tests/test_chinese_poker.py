import pytest

from gamehub.games.chinese_poker import ChinesePokerConfiguration, ChinesePokerGameLogic


@pytest.fixture
def default_config():
    return ChinesePokerConfiguration(num_players=4)


@pytest.fixture
def player_ids():
    return "Alice", "Bob", "Charlie", "Diana"


@pytest.fixture
def game_logic(default_config):
    return ChinesePokerGameLogic(default_config)


@pytest.fixture
def initial_state(game_logic, player_ids):
    return game_logic.initial_state(*player_ids)


def test_chinese_poker_has_proper_game_type(game_logic):
    assert game_logic.game_type == "chinese_poker"


def test_chinese_poker_has_variable_number_of_players():
    config = ChinesePokerConfiguration(num_players=3)
    assert ChinesePokerGameLogic(config).num_players == 3


def test_chinese_poker_starts_with_proper_players(initial_state, player_ids):
    shared_view = initial_state.shared_view()
    assert set(player.player_id for player in shared_view.players) == set(player_ids)


def test_chinese_poker_starts_with_zero_points_for_each_player(initial_state):
    shared_view = initial_state.shared_view()
    assert all(player.num_points == 0 for player in shared_view.players)


def test_chinese_poker_starts_with_zero_cards_for_each_player(initial_state):
    shared_view = initial_state.shared_view()
    assert all(player.num_cards == 0 for player in shared_view.players)
