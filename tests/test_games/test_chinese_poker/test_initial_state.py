from gamehub.games.chinese_poker.status import ChinesePokerStatus


def test_chinese_poker_starts_with_proper_players(
    start_game, player_ids, default_config
):
    shared_view = start_game.shared_view(default_config)
    assert set(player.player_id for player in shared_view.players) == set(player_ids)


def test_chinese_poker_starts_with_zero_points_for_each_player(
    start_game, default_config
):
    shared_view = start_game.shared_view(default_config)
    assert all(player.num_points == 0 for player in shared_view.players)


def test_chinese_poker_starts_with_zero_cards_for_each_player(
    start_game, default_config
):
    shared_view = start_game.shared_view(default_config)
    assert all(player.num_cards == 0 for player in shared_view.players)


def test_chinese_poker_starts_with_status_start_game(start_game, default_config):
    shared_view = start_game.shared_view(default_config)
    assert shared_view.status == ChinesePokerStatus.START_GAME
