import pytest

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.rock_paper_scissors import (
    RPSGameLogic,
    RPSMove,
    RPSPrivateView,
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
    logic = RPSGameLogic()
    with pytest.raises(InvalidMoveError, match="has already selected"):
        _ = logic.make_move(
            after_first_move, RPSMove(player_id="Alice", selection=RPSSelection.PAPER)
        )


def test_rock_paper_scissors_informs_private_selection(after_first_move):
    private_views = list(after_first_move.private_views())
    assert private_views == [("Alice", RPSPrivateView(selection=RPSSelection.ROCK))]
