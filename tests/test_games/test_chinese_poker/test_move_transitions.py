import pytest

from gamehub.core.exceptions import InvalidMoveError
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


def test_valid_move_is_added_to_the_end_of_list_of_move_history(
    await_action, first_move, second_move, make_moves, default_config
):
    next_state = make_moves(await_action, [first_move, second_move])
    shared_view = next_state.shared_view(default_config)
    assert shared_view.move_history == (first_move, second_move)


def test_player_cannot_play_out_of_turn(game_logic, await_action, parse_move):
    with pytest.raises(InvalidMoveError, match="not your turn"):
        game_logic.make_move(await_action, parse_move("Alice", ""))


def test_player_cannot_use_cards_they_do_not_own(game_logic, await_action, parse_move):
    with pytest.raises(InvalidMoveError, match="do not have those cards"):
        game_logic.make_move(
            await_action,
            parse_move("Diana", "3d 3s"),
        )


def test_first_player_of_the_round_cannot_pass(game_logic, await_action, parse_move):
    with pytest.raises(InvalidMoveError, match="cannot pass"):
        game_logic.make_move(await_action, parse_move("Diana", ""))


def test_first_player_of_the_match_must_use_smallest_card(
    game_logic, await_action, parse_move
):
    with pytest.raises(InvalidMoveError, match="must use smallest card"):
        game_logic.make_move(await_action, parse_move("Diana", "4c"))


def test_player_must_use_same_number_of_cards_as_hand_to_beat(
    await_action, parse_move, make_moves
):
    moves = [
        parse_move("Diana", "3d"),
        parse_move("Alice", "5d 5h"),
    ]
    with pytest.raises(InvalidMoveError, match="Must use the same number of cards"):
        make_moves(await_action, moves)


def test_player_must_play_valid_hand(game_logic, await_action, parse_move):
    with pytest.raises(InvalidMoveError, match="Invalid hand"):
        game_logic.make_move(
            await_action,
            parse_move("Diana", "3d 4c"),
        )


def test_player_must_beat_previous_hand(await_action, parse_move, make_moves):
    moves = [
        parse_move("Diana", "3d"),
        parse_move("Alice", "Kc"),
        parse_move("Bob", "Ks"),
    ]
    with pytest.raises(InvalidMoveError, match="does not beat previous hand"):
        make_moves(await_action, moves)
