import pytest

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.chinese_poker import ChinesePokerMove
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


def test_players_cards_are_updated_after_valid_move(
    game_logic, await_action, first_move, initial_cards
):
    next_state = game_logic.make_move(await_action, first_move)
    player_id, private_view = next(next_state.private_views())
    assert len(private_view.cards) == 8
    assert set(private_view.cards) == set(initial_cards[player_id]) - set(
        first_move.cards
    )


def test_move_history_is_updated_after_valid_move(game_logic, await_action, first_move):
    next_state = game_logic.make_move(await_action, first_move)
    shared_view = next_state.shared_view()
    assert shared_view.move_history == (first_move,)


def test_player_cannot_play_out_of_turn(game_logic, await_action):
    with pytest.raises(InvalidMoveError, match="not your turn"):
        game_logic.make_move(
            await_action, ChinesePokerMove(player_id="Alice", cards=())
        )


def test_player_cannot_use_cards_they_do_not_own(game_logic, await_action, parse_hand):
    with pytest.raises(InvalidMoveError, match="do not have those cards"):
        game_logic.make_move(
            await_action,
            ChinesePokerMove(player_id="Diana", cards=(parse_hand("3d 3s"))),
        )


def test_first_player_of_the_round_cannot_pass(game_logic, await_action):
    with pytest.raises(InvalidMoveError, match="cannot pass"):
        game_logic.make_move(
            await_action, ChinesePokerMove(player_id="Diana", cards=())
        )


def test_first_player_of_the_match_must_use_smallest_card(
    game_logic, await_action, parse_hand
):
    with pytest.raises(InvalidMoveError, match="must use smallest card"):
        game_logic.make_move(
            await_action, ChinesePokerMove(player_id="Diana", cards=(parse_hand("4c")))
        )


def test_player_must_use_same_number_of_cards_as_hand_to_beat(
    await_action, parse_hand, make_moves
):
    moves = [
        ChinesePokerMove(player_id="Diana", cards=(parse_hand("3d"))),
        ChinesePokerMove(player_id="Alice", cards=(parse_hand("5d 5h"))),
    ]
    with pytest.raises(InvalidMoveError, match="Must use the same number of cards"):
        make_moves(await_action, moves)


def test_player_must_play_valid_hand(game_logic, await_action, parse_hand):
    with pytest.raises(InvalidMoveError, match="Invalid hand"):
        game_logic.make_move(
            await_action,
            ChinesePokerMove(player_id="Diana", cards=(parse_hand("3d 4c"))),
        )


def test_player_must_beat_previous_hand(await_action, parse_hand, make_moves):
    moves = [
        ChinesePokerMove(player_id="Diana", cards=(parse_hand("3d"))),
        ChinesePokerMove(player_id="Alice", cards=(parse_hand("Kc"))),
        ChinesePokerMove(player_id="Bob", cards=(parse_hand("Ks"))),
    ]
    with pytest.raises(InvalidMoveError, match="does not beat previous hand"):
        make_moves(await_action, moves)
