import pytest

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.chinese_poker.status import ChinesePokerStatus


@pytest.mark.parametrize(
    "state", ["start_game", "start_match", "deal_cards", "start_round"]
)
def test_state_does_not_support_player_move(request, state, first_move, game_logic):
    state = request.getfixturevalue(state)
    with pytest.raises(InvalidMoveError, match="Cannot make move at this time"):
        game_logic.make_move(state, first_move)


def test_await_player_action_transitions_to_end_turn_after_valid_move(
    game_logic, await_action, first_move
):
    next_state = game_logic.make_move(await_action, first_move)
    assert next_state.status == ChinesePokerStatus.END_TURN
