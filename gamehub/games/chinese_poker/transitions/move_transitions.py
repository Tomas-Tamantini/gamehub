from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.status import ChinesePokerStatus
from gamehub.games.chinese_poker.transitions.move_validator import (
    MoveContext,
    validate_move,
)


def _players_after_move(state: ChinesePokerState, move: ChinesePokerMove):
    for player in state.players:
        if player.player_id == move.player_id:
            yield player.remove_cards(move.cards)
        else:
            yield player


def state_after_move(
    state: ChinesePokerState,
    move: ChinesePokerMove,
    configuration: ChinesePokerConfiguration,
) -> ChinesePokerState:
    validate_move(MoveContext(state, move, configuration))

    return ChinesePokerState(
        status=ChinesePokerStatus.END_TURN,
        players=tuple(_players_after_move(state, move)),
        current_player_idx=state.current_player_idx,
        move_history=state.move_history + (move,),
    )
