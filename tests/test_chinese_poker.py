import pytest

from gamehub.games.chinese_poker import ChinesePokerConfiguration, ChinesePokerGameLogic


@pytest.fixture
def default_config():
    return ChinesePokerConfiguration(num_players=4)


@pytest.fixture
def game_logic(default_config):
    return ChinesePokerGameLogic(default_config)


def test_chinese_poker_has_proper_game_type(game_logic):
    assert game_logic.game_type == "chinese_poker"


def test_chinese_poker_has_variable_number_of_players():
    config = ChinesePokerConfiguration(num_players=3)
    assert ChinesePokerGameLogic(config).num_players == 3
