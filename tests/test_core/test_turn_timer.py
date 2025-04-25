import asyncio
from unittest.mock import Mock

import pytest

from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)
from gamehub.core.events.timer_events import TurnTimeout, TurnTimerAlert
from gamehub.core.turn_timer import TurnTimer, TurnTimerRegistry


@pytest.fixture
def spy_timer():
    def _create_spy_timer(room_id):
        timer = Mock(spec=TurnTimer)
        timer.room_id = room_id
        return timer

    return _create_spy_timer


@pytest.fixture
def spy_timers(spy_timer):
    return [spy_timer(room_id=1), spy_timer(room_id=2)]


@pytest.fixture
def registry(spy_timers):
    return TurnTimerRegistry(spy_timers)


def test_turn_timer_registry_resets_proper_turn_timer_on_game_start(
    spy_timers, registry
):
    registry.handle_game_start(GameStarted(room_id=1))
    spy_timers[0].reset.assert_called_once()
    spy_timers[1].reset.assert_not_called()


def test_turn_timer_registry_resets_proper_turn_timer_on_game_end(spy_timers, registry):
    registry.handle_game_end(GameEnded(room_id=1))
    spy_timers[0].reset.assert_called_once()
    spy_timers[1].reset.assert_not_called()


@pytest.mark.asyncio
async def test_turn_timer_registry_delegates_turn_started_event_to_proper_turn_timer(
    spy_timers, registry
):
    await registry.handle_turn_start(TurnStarted(room_id=1, player_id="player1"))
    spy_timers[0].start.assert_called_once_with("player1")
    spy_timers[1].start.assert_not_called()


def test_turn_timer_registry_cancels_turn_timer_on_turn_end(spy_timers, registry):
    registry.handle_turn_end(TurnEnded(room_id=1, player_id="player1"))
    spy_timers[0].cancel.assert_called_once_with("player1")
    spy_timers[1].cancel.assert_not_called()


@pytest.fixture
def timer_alert_spy(event_spy):
    return event_spy(TurnTimerAlert, TurnTimeout)


# TODO: Speed up test. Use monkeypatching?
@pytest.mark.asyncio
async def test_turn_timer_schedules_alert_events_and_timeout_event(
    timer_alert_spy, event_bus
):
    timer = TurnTimer(
        event_bus, room_id=1, timeout_seconds=5, reminders_at_seconds_remaining=(1, 2)
    )
    await timer.start(player_id="player1")
    await asyncio.sleep(6)
    assert timer_alert_spy == [
        TurnTimerAlert(room_id=1, player_id="player1", time_left_seconds=2),
        TurnTimerAlert(room_id=1, player_id="player1", time_left_seconds=1),
        TurnTimeout(room_id=1, player_id="player1"),
    ]
