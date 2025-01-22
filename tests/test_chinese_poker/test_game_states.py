import pytest

from gamehub.games.chinese_poker.status import ChinesePokerStatus


@pytest.mark.parametrize("state", ["start_game", "start_match", "start_round"])
def test_state_doesnt_have_private_views(request, state):
    state = request.getfixturevalue(state)
    assert not list(state.private_views())


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


@pytest.mark.parametrize("state", ["start_game", "start_match", "deal_cards"])
def test_state_doesnt_have_current_player(request, state):
    state = request.getfixturevalue(state)
    assert state.shared_view().current_player_id is None


@pytest.mark.parametrize("state", ["start_round", "start_turn", "await_action"])
def test_state_has_current_player(request, state):
    state = request.getfixturevalue(state)
    assert state.shared_view().current_player_id == "Diana"
