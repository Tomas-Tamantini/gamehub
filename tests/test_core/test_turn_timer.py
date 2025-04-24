from unittest.mock import Mock

from gamehub.core.events.game_state_update import GameEnded, GameStarted
from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


def test_turn_timer_registry_resets_proper_turn_timer_on_game_start():
    spy_timer_a = Mock(spec=TurnTimer)
    spy_timer_a.room_id = 123
    spy_timer_b = Mock(spec=TurnTimer)
    spy_timer_b.room_id = 456
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_game_start(GameStarted(room_id=123))
    spy_timer_a.reset.assert_called_once()
    spy_timer_b.reset.assert_not_called()


def test_turn_timer_registry_resets_proper_turn_timer_on_game_end():
    spy_timer_a = Mock(spec=TurnTimer)
    spy_timer_a.room_id = 123
    spy_timer_b = Mock(spec=TurnTimer)
    spy_timer_b.room_id = 456
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_game_end(GameEnded(room_id=123))
    spy_timer_a.reset.assert_called_once()
    spy_timer_b.reset.assert_not_called()
