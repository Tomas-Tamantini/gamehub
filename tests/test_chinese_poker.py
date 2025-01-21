from gamehub.games.chinese_poker import ChinesePokerGameLogic


def test_chinese_poker_has_proper_game_type():
    assert ChinesePokerGameLogic().game_type == "chinese_poker"
