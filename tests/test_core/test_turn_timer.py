from unittest.mock import Mock

from gamehub.core.events.game_state_update import GameStarted
from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


def test_turn_timer_registry_resets_proper_turn_timer_on_game_start():
    mock_timer_a = Mock(spec=TurnTimer)
    mock_timer_a.room_id = 123
    mock_timer_b = Mock(spec=TurnTimer)
    mock_timer_b.room_id = 456
    registry = TurnTimerRegistry(turn_timers=[mock_timer_a, mock_timer_b])
    registry.handle_game_start(GameStarted(room_id=123))
    mock_timer_a.reset.assert_called_once()
    mock_timer_b.reset.assert_not_called()
