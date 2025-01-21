from gamehub.games.chinese_poker.status import ChinesePokerStatus


def test_start_game_transitions_to_start_match(game_logic, start_game):
    start_match = game_logic.next_automated_state(start_game)
    assert start_match.shared_view().status == ChinesePokerStatus.START_MATCH


def test_start_match_transitions_to_deal_cards(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    assert deal_cards.shared_view().status == ChinesePokerStatus.DEAL_CARDS


def test_start_game_to_start_match_transition_preservers_players(
    game_logic, start_game
):
    start_match = game_logic.next_automated_state(start_game)
    assert start_game.players == start_match.players
