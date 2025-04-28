import pytest

from gamehub.games.chinese_poker.status import ChinesePokerStatus


@pytest.mark.parametrize(
    "state",
    [
        "start_game",
        "start_match",
        "deal_cards",
        "start_round",
        "start_turn",
        "end_turn",
        "end_last_turn",
        "end_round",
        "end_last_round",
        "end_match",
        "update_points",
        "last_points_update",
    ],
)
def test_state_after_timeout_is_null_if_current_state_not_awaiting_action(
    request, game_logic, state
):
    current_state = request.getfixturevalue(state)
    assert game_logic.state_after_timeout(current_state, "Alice") is None


def test_state_after_timeout_is_null_if_not_players_turn(game_logic, await_action):
    next_state = game_logic.state_after_timeout(await_action, "Alice")
    assert next_state is None


def test_state_after_timeout_is_player_passing_if_they_can_pass(
    game_logic, await_second_action
):
    next_state = game_logic.state_after_timeout(await_second_action, "Alice")
    assert next_state.status == ChinesePokerStatus.END_TURN
    assert next_state.move_history[-1].cards == tuple()
    assert next_state.move_history[-1].is_bot_move


def test_state_after_timeout_is_player_playing_smallest_card_if_they_cannot_pass(
    game_logic, await_action, parse_hand
):
    next_state = game_logic.state_after_timeout(await_action, "Diana")
    assert next_state.status == ChinesePokerStatus.END_TURN
    assert next_state.move_history[-1].cards == parse_hand("3d")
    assert next_state.move_history[-1].is_bot_move
