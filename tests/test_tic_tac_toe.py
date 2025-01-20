import pytest
from pydantic import ValidationError

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove
from gamehub.games.tic_tac_toe.game_state import TicTacToeState
from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


@pytest.fixture
def initial_state():
    return TicTacToeGameLogic().initial_state("Alice", "Bob")


@pytest.fixture
def after_first_move(initial_state):
    return TicTacToeGameLogic().make_move(
        initial_state, TicTacToeMove(player_id="Alice", cell_index=0)
    )


@pytest.fixture
def tie_game():
    return TicTacToeState(
        players=(
            TicTacToePlayer(player_id="Alice", selections={0, 1, 5, 6, 8}),
            TicTacToePlayer(player_id="Bob", selections={2, 3, 4, 7}),
        )
    )


@pytest.mark.parametrize("bad_idx", [-1, 9])
def test_tic_tac_toe_cell_index_must_be_between_0_and_8(bad_idx):
    with pytest.raises(ValidationError, match="cell_index"):
        TicTacToeMove(player_id="p1", cell_idx=bad_idx)


def test_tic_tac_toe_has_two_players():
    assert TicTacToeGameLogic().num_players == 2


def test_tic_tac_toe_has_proper_game_type():
    assert TicTacToeGameLogic().game_type == "tic_tac_toe"


def test_tic_tac_toe_starts_with_empty_board(initial_state):
    shared_view = initial_state.shared_view()
    assert shared_view == TicTacToeView(
        players=(
            TicTacToePlayer(player_id="Alice", selections=set()),
            TicTacToePlayer(player_id="Bob", selections=set()),
        ),
        current_player="Alice",
    )


def test_tic_tac_toe_does_not_allow_player_to_play_out_of_turn(initial_state):
    with pytest.raises(InvalidMoveError, match="Not player's turn"):
        _ = TicTacToeGameLogic().make_move(
            initial_state, TicTacToeMove(player_id="Bob", cell_index=0)
        )


def test_tic_tac_toe_allows_player_to_select_empty_cell(after_first_move):
    shared_view = after_first_move.shared_view()
    assert shared_view == TicTacToeView(
        players=(
            TicTacToePlayer(player_id="Alice", selections={0}),
            TicTacToePlayer(player_id="Bob", selections=set()),
        ),
        current_player="Bob",
    )


def test_tic_tac_toe_cell_cannot_be_selected_twice(after_first_move):
    with pytest.raises(InvalidMoveError, match="already selected"):
        _ = TicTacToeGameLogic().make_move(
            after_first_move, TicTacToeMove(player_id="Bob", cell_index=0)
        )


@pytest.mark.parametrize(
    ("selections_a", "selections_b", "winner"),
    [
        ({0, 1, 2}, {3, 4}, "Alice"),
        ({0, 1, 8}, {3, 4, 5}, "Bob"),
        ({0, 1, 3}, {6, 7, 8}, "Bob"),
        ({0, 3, 6}, {1, 2}, "Alice"),
        ({1, 4, 7}, {0, 2}, "Alice"),
        ({2, 5, 8}, {1, 0}, "Alice"),
        ({0, 4, 8}, {1, 2}, "Alice"),
        ({0, 1, 8}, {2, 4, 6}, "Bob"),
    ],
)
def test_player_wins_tic_tac_toe_if_three_in_a_row(selections_a, selections_b, winner):
    state = TicTacToeState(
        players=(
            TicTacToePlayer(player_id="Alice", selections=selections_a),
            TicTacToePlayer(player_id="Bob", selections=selections_b),
        )
    )
    shared_view = state.shared_view()
    assert shared_view.is_over
    assert shared_view.winner == winner


def test_players_tie_on_tic_tac_toe_if_no_three_in_a_row(tie_game):
    shared_view = tie_game.shared_view()
    assert shared_view.is_over
    assert shared_view.winner is None


def test_players_cannot_make_move_after_game_over():
    state = TicTacToeState(
        players=(
            TicTacToePlayer(player_id="Alice", selections={0, 1, 2}),
            TicTacToePlayer(player_id="Bob", selections={3, 4}),
        )
    )
    with pytest.raises(InvalidMoveError, match="Game is over"):
        _ = TicTacToeGameLogic().make_move(
            state, TicTacToeMove(player_id="Bob", cell_index=5)
        )
