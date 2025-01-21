def test_chinese_poker_starts_with_proper_players(initial_state, player_ids):
    shared_view = initial_state.shared_view()
    assert set(player.player_id for player in shared_view.players) == set(player_ids)


def test_chinese_poker_starts_with_zero_points_for_each_player(initial_state):
    shared_view = initial_state.shared_view()
    assert all(player.num_points == 0 for player in shared_view.players)


def test_chinese_poker_starts_with_zero_cards_for_each_player(initial_state):
    shared_view = initial_state.shared_view()
    assert all(player.num_cards == 0 for player in shared_view.players)
