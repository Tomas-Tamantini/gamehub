import pytest
from pydantic import ValidationError

from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove
from gamehub.games.tic_tac_toe.player import TicTacToePlayer
from gamehub.games.tic_tac_toe.views import TicTacToeView


@pytest.mark.parametrize("bad_idx", [-1, 9])
def test_tic_tac_toe_cell_index_must_be_between_0_and_8(bad_idx):
    with pytest.raises(ValidationError, match="cell_index"):
        TicTacToeMove(player_id="p1", cell_idx=bad_idx)


def test_tic_tac_toe_has_two_players():
    assert TicTacToeGameLogic().num_players == 2


def test_tic_tac_toe_starts_with_empty_board():
    logic = TicTacToeGameLogic()
    state = logic.initial_state("Alice", "Bob")
    shared_view = state.shared_view()
    assert shared_view == TicTacToeView(
        players=(
            TicTacToePlayer(player_id="Alice", selections=set()),
            TicTacToePlayer(player_id="Bob", selections=set()),
        )
    )
