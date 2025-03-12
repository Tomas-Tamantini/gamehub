import pytest

from gamehub.games.chinese_poker.status import ChinesePokerStatus


@pytest.mark.parametrize(
    "state",
    [
        "start_game",
        "start_match",
        "start_round",
        "start_turn",
        "end_round",
        "end_last_round",
        "end_match",
        "update_points",
        "last_points_update",
        "end_game",
    ],
)
def test_state_doesnt_yield_private_views(request, state):
    state = request.getfixturevalue(state)
    assert not list(state.private_views())


@pytest.mark.parametrize(
    "state",
    [
        "start_game",
        "start_match",
        "start_round",
        "start_turn",
        "end_round",
        "end_last_round",
        "end_match",
        "update_points",
        "last_points_update",
        "end_game",
    ],
)
def test_state_can_be_queried_for_its_private_views(request, state):
    state = request.getfixturevalue(state)
    private_view = state.query_private_view("Alice")
    assert private_view.status == state.status
    assert private_view.cards == state.players[0].cards


def test_each_player_receives_their_private_cards_after_dealing(
    deal_cards, player_ids, initial_cards
):
    private_views = list(deal_cards.private_views())
    assert len(private_views) == 4
    ids, views = list(zip(*private_views))
    assert set(player_ids) == set(ids)
    assert all(
        view.cards == initial_cards[player_id] for player_id, view in private_views
    )
    assert all(view.status == ChinesePokerStatus.DEAL_CARDS for view in views)


def test_player_receives_their_private_cards_on_their_turn(await_action, initial_cards):
    private_views = list(await_action.private_views())
    assert len(private_views) == 1
    player_id, view = private_views[0]
    assert player_id == "Diana"
    assert view.cards == initial_cards["Diana"]
    assert view.status == ChinesePokerStatus.AWAIT_PLAYER_ACTION


def test_player_receives_their_private_cards_after_their_turn(
    end_turn, initial_cards, first_move
):
    private_views = list(end_turn.private_views())
    assert len(private_views) == 1
    player_id, view = private_views[0]
    assert player_id == "Diana"
    assert set(view.cards) == set(initial_cards["Diana"]) - set(first_move.cards)
    assert view.status == ChinesePokerStatus.END_TURN


@pytest.mark.parametrize(
    "state", ["start_round", "start_turn", "await_action", "end_turn"]
)
def test_state_maintains_current_player(request, state, default_config):
    state = request.getfixturevalue(state)
    assert state.shared_view(default_config).current_player_id == "Diana"


@pytest.mark.parametrize("state", ["end_round"])
def test_state_increments_current_player(request, state, default_config):
    state = request.getfixturevalue(state)
    assert state.shared_view(default_config).current_player_id == "Alice"


@pytest.mark.parametrize("state", ["start_round", "start_turn", "await_action"])
def test_state_is_not_terminal_if_not_game_over(request, state):
    state = request.getfixturevalue(state)
    assert not state.is_terminal()


def test_state_is_terminal_if_game_over(end_game):
    assert end_game.is_terminal()


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("start_game", [0, 0, 0, 0]),
        ("start_match", [0, 0, 0, 0]),
        ("start_round", [0, 0, 0, 0]),
        ("start_turn", [0, 0, 0, 0]),
        ("await_action", [0, 0, 0, 0]),
        ("end_turn", [0, 0, 0, 0]),
        ("end_round", [0, 0, 0, 0]),
        ("end_match", [0, 0, 0, 0]),
        ("update_points", [425, -275, -75, -75]),
        ("end_game", [550, 350, -850, -50]),
    ],
)
def test_partial_results_are_sent_with_each_game_state(
    request, state, expected, default_config
):
    state = request.getfixturevalue(state)
    result = [p.partial_credits for p in state.shared_view(default_config).players]
    assert expected == result
