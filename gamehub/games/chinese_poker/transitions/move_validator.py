from dataclasses import dataclass
from typing import Optional

from gamehub.core.exceptions import InvalidMoveError
from gamehub.games.chinese_poker.configuration import ChinesePokerConfiguration
from gamehub.games.chinese_poker.game_state import ChinesePokerState
from gamehub.games.chinese_poker.hand import hand_value
from gamehub.games.chinese_poker.move import ChinesePokerMove
from gamehub.games.chinese_poker.status import ChinesePokerStatus


@dataclass(frozen=True)
class MoveContext:
    state: ChinesePokerState
    move: ChinesePokerMove
    configuration: ChinesePokerConfiguration


def _status_checker(ctx: MoveContext) -> Optional[str]:
    if ctx.state.status != ChinesePokerStatus.AWAIT_PLAYER_ACTION:
        return "Cannot make move at this time"


def _turn_checker(ctx: MoveContext) -> Optional[str]:
    if ctx.state.current_player_id() != ctx.move.player_id:
        return "It is not your turn"


def _own_cards_checker(ctx: MoveContext) -> Optional[str]:
    if not ctx.state.current_player().has_cards(ctx.move.cards):
        return "You do not have those cards"


def _pass_checker(ctx: MoveContext) -> Optional[str]:
    if ctx.move.is_pass and not ctx.state.move_history:
        return "First player of the round cannot pass"


def _smallest_card_checker(ctx: MoveContext) -> Optional[str]:
    if (
        ctx.state.is_first_turn_of_match(ctx.configuration.cards_per_player)
        and ctx.state.smallest_card() not in ctx.move.cards
    ):
        return "First player of the match must use smallest card"


def _hand_checker(ctx: MoveContext) -> Optional[str]:
    if not ctx.move.is_pass:
        try:
            move_value = hand_value(ctx.move.cards)
        except ValueError as e:
            return str(e)

        if hand_to_beat := ctx.state.hand_to_beat():
            if len(ctx.move.cards) != len(hand_to_beat.cards):
                return "Must use the same number of cards as the hand to beat"
            elif move_value <= hand_value(hand_to_beat.cards):
                return "Hand does not beat previous hand"


def validate_move(move_context: MoveContext):
    checkers = (
        _status_checker,
        _turn_checker,
        _own_cards_checker,
        _pass_checker,
        _smallest_card_checker,
        _hand_checker,
    )
    for checker in checkers:
        if error := checker(move_context):
            raise InvalidMoveError(error)
