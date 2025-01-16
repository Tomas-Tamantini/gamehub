from gamehub.games.rock_paper_scissors import (
    RPSSharedPlayerView,
    RPSSharedView,
    rps_setup,
)


def test_rock_paper_scissors_has_two_players():
    setup = rps_setup()
    assert setup.num_players == 2


def test_rock_paper_scissors_initial_state_has_no_selections():
    setup = rps_setup()
    state = setup.initial_state(["Alice", "Bob"])
    shared_view = state.shared_view()
    assert shared_view == RPSSharedView(
        players=[
            RPSSharedPlayerView(player_id="Alice", selected=False),
            RPSSharedPlayerView(player_id="Bob", selected=False),
        ]
    )
