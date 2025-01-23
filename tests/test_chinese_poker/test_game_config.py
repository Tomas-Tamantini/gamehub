from gamehub.games.chinese_poker import ChinesePokerConfiguration, ChinesePokerGameLogic


def test_chinese_poker_has_proper_game_type(game_logic):
    assert game_logic.game_type == "chinese_poker"


def test_chinese_poker_has_variable_number_of_players():
    config = ChinesePokerConfiguration(
        num_players=3, cards_per_player=10, game_over_point_threshold=10
    )
    assert ChinesePokerGameLogic(config).num_players == 3
