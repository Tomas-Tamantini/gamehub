import pytest

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.rock_paper_scissors import (
    RPSGameLogic,
    RPSMove,
    RPSPlayerView,
    RPSPrivateView,
    RPSResultView,
    RPSSelection,
    RPSSharedPlayerView,
    RPSSharedView,
)


@pytest.fixture
def initial_state():
    logic = RPSGameLogic()
    return logic.initial_state("Alice", "Bob")


@pytest.fixture
def after_first_move(initial_state):
    logic = RPSGameLogic()
    return logic.make_move(
        initial_state, RPSMove(player_id="Alice", selection=RPSSelection.ROCK)
    )


def test_rock_paper_scissors_has_two_players():
    assert RPSGameLogic().num_players == 2


def test_rock_paper_scissors_initial_state_has_no_selections(initial_state):
    shared_view = initial_state.shared_view()
    assert shared_view == RPSSharedView(
        players=[
            RPSSharedPlayerView(player_id="Alice", selected=False),
            RPSSharedPlayerView(player_id="Bob", selected=False),
        ]
    )


def test_rock_paper_scissors_allows_players_to_make_selection(after_first_move):
    shared_view = after_first_move.shared_view()
    assert shared_view == RPSSharedView(
        players=[
            RPSSharedPlayerView(player_id="Alice", selected=True),
            RPSSharedPlayerView(player_id="Bob", selected=False),
        ]
    )


def test_player_cannot_select_twice_in_rock_paper_scisssors(after_first_move):
    with pytest.raises(InvalidMoveError, match="has already selected"):
        _ = RPSGameLogic().make_move(
            after_first_move, RPSMove(player_id="Alice", selection=RPSSelection.PAPER)
        )


def test_rock_paper_scissors_informs_private_selection(after_first_move):
    private_views = list(after_first_move.private_views())
    assert private_views == [("Alice", RPSPrivateView(selection=RPSSelection.ROCK))]


def test_rock_paper_scissors_informs_result_after_both_selected(after_first_move):
    game_over_state = RPSGameLogic().make_move(
        after_first_move, RPSMove(player_id="Bob", selection=RPSSelection.PAPER)
    )
    shared_view = game_over_state.shared_view()
    assert shared_view.result == RPSResultView(
        winner="Bob",
        moves=[
            RPSPlayerView(player_id="Alice", selection=RPSSelection.ROCK),
            RPSPlayerView(player_id="Bob", selection=RPSSelection.PAPER),
        ],
    )


@pytest.mark.parametrize(
    "selection", [RPSSelection.ROCK, RPSSelection.PAPER, RPSSelection.SCISSORS]
)
def test_players_tie_if_both_pick_same_move(initial_state, selection):
    state = initial_state
    for player in ("Alice", "Bob"):
        state = RPSGameLogic().make_move(
            state, RPSMove(player_id=player, selection=selection)
        )
    assert state.shared_view().result.winner is None


@pytest.mark.parametrize(
    ("selection_a", "selection_b"),
    [
        (RPSSelection.PAPER, RPSSelection.ROCK),
        (RPSSelection.SCISSORS, RPSSelection.PAPER),
        (RPSSelection.ROCK, RPSSelection.SCISSORS),
    ],
)
def test_rock_paper_scissors_beat_each_other_cyclically(
    initial_state, selection_a, selection_b
):
    state = initial_state
    for player, selection in [("Alice", selection_a), ("Bob", selection_b)]:
        state = RPSGameLogic().make_move(
            state, RPSMove(player_id=player, selection=selection)
        )
    assert state.shared_view().result.winner == "Alice"
