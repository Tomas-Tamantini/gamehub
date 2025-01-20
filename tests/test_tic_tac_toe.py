import pytest
from pydantic import ValidationError
from gamehub.core.exceptions import InvalidMoveError

from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove
from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


@pytest.fixture
def initial_state():
    return TicTacToeGameLogic().initial_state("Alice", "Bob")


@pytest.mark.parametrize("bad_idx", [-1, 9])
def test_tic_tac_toe_cell_index_must_be_between_0_and_8(bad_idx):
    with pytest.raises(ValidationError, match="cell_index"):
        TicTacToeMove(player_id="p1", cell_idx=bad_idx)


def test_tic_tac_toe_has_two_players():
    assert TicTacToeGameLogic().num_players == 2


def test_tic_tac_toe_starts_with_empty_board(initial_state):
    shared_view = initial_state.shared_view()
    assert shared_view == TicTacToeView(
        players=(
            TicTacToePlayer(player_id="Alice", selections=set()),
            TicTacToePlayer(player_id="Bob", selections=set()),
        )
    )


def test_tic_tac_toe_does_not_allow_player_to_play_out_of_turn(initial_state):
    with pytest.raises(InvalidMoveError, match="Not player's turn"):
        _ = TicTacToeGameLogic().make_move(
            initial_state, TicTacToeMove(player_id="Bob", cell_index=0)
        )
