import pytest

from gamehub.games.chinese_poker.status import ChinesePokerStatus


@pytest.mark.parametrize(
    ("state_before", "expected_status"),
    [
        ("start_game", ChinesePokerStatus.START_MATCH),
        ("start_match", ChinesePokerStatus.DEAL_CARDS),
        ("deal_cards", ChinesePokerStatus.START_ROUND),
        ("start_round", ChinesePokerStatus.START_TURN),
        ("start_turn", ChinesePokerStatus.AWAIT_PLAYER_ACTION),
        ("end_turn", ChinesePokerStatus.START_TURN),
        ("end_last_turn", ChinesePokerStatus.END_ROUND),
        ("end_round", ChinesePokerStatus.START_ROUND),
        ("end_last_round", ChinesePokerStatus.END_MATCH),
        ("end_match", ChinesePokerStatus.UPDATE_POINTS),
        ("update_points", ChinesePokerStatus.START_MATCH),
        ("last_points_update", ChinesePokerStatus.END_GAME),
    ],
)
def test_state_transitions_automatically(
    request, game_logic, state_before, expected_status
):
    state_before = request.getfixturevalue(state_before)
    state_after = game_logic.next_automated_state(state_before)
    assert state_after.shared_view().status == expected_status


@pytest.mark.parametrize("state", ["await_action", "end_game"])
def test_state_does_not_transition_automatically(request, game_logic, state):
    no_transition = request.getfixturevalue(state)
    assert game_logic.next_automated_state(no_transition) is None


def test_each_player_receives_dealt_cards(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    assert all(len(player.cards) == 13 for player in deal_cards.players)


def test_players_receive_cards_without_repetition(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    cards = {card for player in deal_cards.players for card in player.cards}
    assert len(cards) == 52


def test_end_turn_increments_turn_if_not_round_end(game_logic, end_turn):
    start_turn = game_logic.next_automated_state(end_turn)
    assert start_turn.shared_view().current_player_id == "Alice"


def test_player_who_won_last_round_starts_next_one(game_logic, end_last_turn):
    end_round = game_logic.next_automated_state(end_last_turn)
    assert end_round.shared_view().current_player_id == "Alice"


def test_points_are_updated_after_match_end(update_points):
    expected_points = [0, 7, 5, 5]
    assert [
        player.num_points for player in update_points.shared_view().players
    ] == expected_points


def test_cards_are_reset_after_match_end(update_points):
    assert all(player.num_cards == 0 for player in update_points.shared_view().players)


def test_player_with_the_smallest_card_starts_first_round(start_round):
    assert start_round.current_player_id() == "Diana"


@pytest.mark.parametrize(
    "state_before",
    [
        "start_game",
        "start_match",
        "deal_cards",
        "start_round",
        "start_turn",
        "end_turn",
        "end_last_turn",
        "end_round",
        "end_match",
        "update_points",
    ],
)
def test_transition_preserves_players_order(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert all(
        before.player_id == after.player_id
        for before, after in zip(state_before.players, next_state.players)
    )


@pytest.mark.parametrize(
    "state_before",
    [
        "start_game",
        "start_match",
        "deal_cards",
        "start_round",
        "start_turn",
        "end_turn",
        "end_last_turn",
        "end_round",
        "update_points",
    ],
)
def test_transition_preserves_players_num_points(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert all(
        before.num_points == after.num_points
        for before, after in zip(state_before.players, next_state.players)
    )


@pytest.mark.parametrize(
    "state_before",
    [
        "start_game",
        "deal_cards",
        "start_round",
        "start_turn",
        "end_turn",
        "end_last_turn",
        "end_round",
    ],
)
def test_transition_preserves_players_cards(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert all(
        before.cards == after.cards
        for before, after in zip(state_before.players, next_state.players)
    )


@pytest.mark.parametrize(
    "state_before",
    ["start_game", "start_match", "end_match", "update_points"],
)
def test_transition_resets_current_turn(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert next_state.current_player_id() is None


@pytest.mark.parametrize(
    "state_before",
    [
        "start_game",
        "start_match",
        "deal_cards",
        "start_round",
        "end_round",
        "end_match",
        "update_points",
    ],
)
def test_transition_resets_move_history(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert not next_state.move_history


@pytest.mark.parametrize("state_before", ["start_round", "start_turn", "end_round"])
def test_transition_preserves_current_turn(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert state_before.current_player_id() == next_state.current_player_id()


@pytest.mark.parametrize("state_before", ["start_turn", "end_turn", "end_last_turn"])
def test_transition_preserves_move_history(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert state_before.move_history == next_state.move_history
