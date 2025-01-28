from functools import partial
from typing import Optional

from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.playing_cards import deal_hands


def _from_start_game(state: ChinesePokerState) -> ChinesePokerState:
    return ChinesePokerState(
        status=ChinesePokerStatus.START_MATCH,
        players=state.players,
    )


def _from_start_match(
    state: ChinesePokerState, configuration: ChinesePokerConfiguration
) -> ChinesePokerState:
    hands = deal_hands(
        num_hands=configuration.num_players,
        hand_size=configuration.cards_per_player,
    )
    return ChinesePokerState(
        status=ChinesePokerStatus.DEAL_CARDS,
        players=[p.deal_cards(hand) for p, hand in zip(state.players, hands)],
    )


def _from_deal_cards(state: ChinesePokerState) -> ChinesePokerState:
    return ChinesePokerState(
        status=ChinesePokerStatus.START_ROUND,
        players=state.players,
        current_player_idx=state.idx_of_player_with_smallest_card(),
    )


def _from_start_round(state: ChinesePokerState) -> ChinesePokerState:
    return ChinesePokerState(
        status=ChinesePokerStatus.START_TURN,
        players=state.players,
        current_player_idx=state.current_player_idx,
    )


def _from_start_turn(state: ChinesePokerState) -> ChinesePokerState:
    return ChinesePokerState(
        status=ChinesePokerStatus.AWAIT_PLAYER_ACTION,
        players=state.players,
        current_player_idx=state.current_player_idx,
        move_history=state.move_history,
    )


def _from_end_turn(state: ChinesePokerState) -> ChinesePokerState:
    if state.last_players_passed() or state.next_player_has_zero_cards():
        return ChinesePokerState(
            status=ChinesePokerStatus.END_ROUND,
            players=state.players,
            current_player_idx=state.next_player_idx(),
        )
    else:
        return ChinesePokerState(
            status=ChinesePokerStatus.START_TURN,
            players=state.players,
            current_player_idx=state.next_player_idx(),
            move_history=state.move_history,
        )


def _from_end_round(state: ChinesePokerState) -> ChinesePokerState:
    if state.some_player_has_zero_cards():
        return ChinesePokerState(
            status=ChinesePokerStatus.END_MATCH,
            players=state.players,
        )
    else:
        return ChinesePokerState(
            status=ChinesePokerStatus.START_ROUND,
            players=state.players,
            current_player_idx=state.current_player_idx,
        )


def _from_end_match(state: ChinesePokerState) -> ChinesePokerState:
    return ChinesePokerState(
        status=ChinesePokerStatus.UPDATE_POINTS,
        players=tuple(p.increment_points() for p in state.players),
    )


def _from_update_points(
    state: ChinesePokerState, configuration: ChinesePokerConfiguration
) -> ChinesePokerState:
    if state.max_points() < configuration.game_over_point_threshold:
        return ChinesePokerState(
            status=ChinesePokerStatus.START_MATCH,
            players=state.players,
        )
    else:
        return ChinesePokerState(
            status=ChinesePokerStatus.END_GAME,
            players=state.players,
        )


def next_automated_state(
    state: ChinesePokerState, configuration: ChinesePokerConfiguration
) -> Optional[ChinesePokerState]:
    transitions = {
        ChinesePokerStatus.START_GAME: _from_start_game,
        ChinesePokerStatus.START_MATCH: partial(
            _from_start_match, configuration=configuration
        ),
        ChinesePokerStatus.DEAL_CARDS: _from_deal_cards,
        ChinesePokerStatus.START_ROUND: _from_start_round,
        ChinesePokerStatus.START_TURN: _from_start_turn,
        ChinesePokerStatus.END_TURN: _from_end_turn,
        ChinesePokerStatus.END_ROUND: _from_end_round,
        ChinesePokerStatus.END_MATCH: _from_end_match,
        ChinesePokerStatus.UPDATE_POINTS: partial(
            _from_update_points, configuration=configuration
        ),
    }
    if state.status in transitions:
        return transitions[state.status](state)
