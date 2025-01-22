import pytest


@pytest.mark.parametrize("state", ["start_game", "start_match", "start_round"])
def test_state_doesnt_have_private_views(request, state):
    state = request.getfixturevalue(state)
    assert not list(state.private_views())


def test_each_player_receives_their_private_cards_after_dealing(deal_cards, player_ids):
    state = deal_cards
    private_views = list(state.private_views())
    assert len(private_views) == 4
    ids, views = list(zip(*private_views))
    assert set(player_ids) == set(ids)
    assert all(len(view.cards) == 13 for view in views)


@pytest.mark.parametrize("state", ["start_game", "start_match", "deal_cards"])
def test_state_doesnt_have_current_player(request, state):
    state = request.getfixturevalue(state)
    assert state.shared_view().current_player_id is None


@pytest.mark.parametrize("state", ["start_round"])
def test_state_has_current_player(request, state):
    state = request.getfixturevalue(state)
    assert state.shared_view().current_player_id == "Diana"
