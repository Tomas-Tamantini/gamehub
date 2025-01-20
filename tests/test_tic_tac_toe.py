from gamehub.games.tic_tac_toe import TicTacToeMove
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize("bad_idx", [-1, 9])
def test_tic_tac_toe_cell_index_must_be_between_0_and_8(bad_idx):
    with pytest.raises(ValidationError, match="cell_index"):
        TicTacToeMove(player_id="p1", cell_idx=bad_idx)
