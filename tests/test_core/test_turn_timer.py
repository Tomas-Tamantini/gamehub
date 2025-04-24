from unittest.mock import Mock

import pytest

from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)
from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


@pytest.fixture
def spy_timer():
    def _create_spy_timer(room_id):
        timer = Mock(spec=TurnTimer)
        timer.room_id = room_id
        return timer

    return _create_spy_timer


def test_turn_timer_registry_resets_proper_turn_timer_on_game_start(spy_timer):
    spy_timer_a = spy_timer(123)
    spy_timer_b = spy_timer(456)
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_game_start(GameStarted(room_id=123))
    spy_timer_a.reset.assert_called_once()
    spy_timer_b.reset.assert_not_called()


def test_turn_timer_registry_resets_proper_turn_timer_on_game_end(spy_timer):
    spy_timer_a = spy_timer(123)
    spy_timer_b = spy_timer(456)
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_game_end(GameEnded(room_id=123))
    spy_timer_a.reset.assert_called_once()
    spy_timer_b.reset.assert_not_called()


def test_turn_timer_registry_delegates_turn_started_event_to_proper_turn_timer(
    spy_timer,
):
    spy_timer_a = spy_timer(123)
    spy_timer_b = spy_timer(456)
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_turn_start(TurnStarted(room_id=123, player_id="player1"))
    spy_timer_a.start.assert_called_once_with("player1")
    spy_timer_b.start.assert_not_called()


def test_turn_timer_registry_cancels_turn_timer_on_turn_end(spy_timer):
    spy_timer_a = spy_timer(123)
    spy_timer_b = spy_timer(456)
    registry = TurnTimerRegistry(turn_timers=[spy_timer_a, spy_timer_b])
    registry.handle_turn_end(TurnEnded(room_id=123, player_id="player1"))
    spy_timer_a.cancel.assert_called_once_with("player1")
    spy_timer_b.cancel.assert_not_called()
