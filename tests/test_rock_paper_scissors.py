from gamehub.games.rock_paper_scissors import (
    RPSGameLogic,
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
