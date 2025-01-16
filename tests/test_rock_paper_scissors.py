from gamehub.games.rock_paper_scissors import (
    RPSGameLogic,
    RPSMove,
    RPSPrivateView,
    RPSSelection,
    RPSSharedPlayerView,
    RPSSharedView,
)


def test_rock_paper_scissors_has_two_players():
    assert RPSGameLogic().num_players == 2


def test_rock_paper_scissors_initial_state_has_no_selections():
    logic = RPSGameLogic()
    state = logic.initial_state("Alice", "Bob")
    shared_view = state.shared_view()
    assert shared_view == RPSSharedView(
        players=[
            RPSSharedPlayerView(player_id="Alice", selected=False),
            RPSSharedPlayerView(player_id="Bob", selected=False),
        ]
    )


def test_rock_paper_scissors_allows_players_to_make_selection():
    logic = RPSGameLogic()
    state = logic.initial_state("Alice", "Bob")
    state = logic.make_move(
        state, RPSMove(player_id="Alice", selection=RPSSelection.ROCK)
    )
    shared_view = state.shared_view()
    assert shared_view == RPSSharedView(
        players=[
            RPSSharedPlayerView(player_id="Alice", selected=True),
            RPSSharedPlayerView(player_id="Bob", selected=False),
        ]
    )


def test_rock_paper_scissors_informs_private_selection():
    logic = RPSGameLogic()
    state = logic.initial_state("Alice", "Bob")
    state = logic.make_move(
        state, RPSMove(player_id="Alice", selection=RPSSelection.ROCK)
    )
    private_views = list(state.private_views())
    assert private_views == [("Alice", RPSPrivateView(selection=RPSSelection.ROCK))]
