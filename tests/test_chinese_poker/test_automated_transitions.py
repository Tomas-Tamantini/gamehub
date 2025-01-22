import pytest

from gamehub.games.chinese_poker.status import ChinesePokerStatus


def test_start_game_transitions_to_start_match(game_logic, start_game):
    start_match = game_logic.next_automated_state(start_game)
    assert start_match.shared_view().status == ChinesePokerStatus.START_MATCH


def test_start_match_transitions_to_deal_cards(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    assert deal_cards.shared_view().status == ChinesePokerStatus.DEAL_CARDS


def test_deal_cards_transitions_to_start_round(game_logic, deal_cards):
    start_round = game_logic.next_automated_state(deal_cards)
    assert start_round.shared_view().status == ChinesePokerStatus.START_ROUND


def test_start_round_transitions_to_start_turn(game_logic, start_round):
    start_turn = game_logic.next_automated_state(start_round)
    assert start_turn.shared_view().status == ChinesePokerStatus.START_TURN


def test_start_turn_transitions_to_await_player_action(game_logic, start_turn):
    await_action = game_logic.next_automated_state(start_turn)
    assert await_action.shared_view().status == ChinesePokerStatus.AWAIT_PLAYER_ACTION


def test_each_player_receives_dealt_cards(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    assert all(len(player.cards) == 13 for player in deal_cards.players)


def test_players_receive_cards_without_repetition(game_logic, start_match):
    deal_cards = game_logic.next_automated_state(start_match)
    cards = {card for player in deal_cards.players for card in player.cards}
    assert len(cards) == 52


def test_player_with_the_smallest_card_starts_first_round(start_round):
    assert start_round.current_player_id() == "Diana"


def test_await_action_does_not_transition_automatically(game_logic, await_action):
    assert game_logic.next_automated_state(await_action) is None


@pytest.mark.parametrize(
    "state_before",
    ["start_game", "start_match", "deal_cards", "start_round", "start_turn"],
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
    ["start_game", "start_match", "deal_cards", "start_round", "start_turn"],
)
def test_transition_preserves_players_num_points(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert all(
        before.num_points == after.num_points
        for before, after in zip(state_before.players, next_state.players)
    )


@pytest.mark.parametrize(
    "state_before", ["start_game", "deal_cards", "start_round", "start_turn"]
)
def test_transition_preserves_players_cards(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert all(
        before.cards == after.cards
        for before, after in zip(state_before.players, next_state.players)
    )


@pytest.mark.parametrize("state_before", ["start_game", "start_match"])
def test_transition_resets_current_turn(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert next_state.current_player_id() is None


@pytest.mark.parametrize(
    "state_before", ["start_game", "start_match", "deal_cards", "start_round"]
)
def test_transition_resets_move_history(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert not next_state.move_history


@pytest.mark.parametrize("state_before", ["start_round", "start_turn"])
def test_transition_preserves_current_turn(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert state_before.current_player_id() == next_state.current_player_id()


@pytest.mark.parametrize("state_before", ["start_turn"])
def test_transition_preserves_move_history(request, game_logic, state_before):
    state_before = request.getfixturevalue(state_before)
    next_state = game_logic.next_automated_state(state_before)
    assert state_before.move_history == next_state.move_history
