from unittest.mock import Mock

import pytest

from gamehub.core.event_scheduler import EventScheduler
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


def test_turn_timer_registry_delegates_turn_started_event_to_proper_turn_timer(
    spy_timers, registry
):
    registry.handle_turn_start(
        TurnStarted(room_id=1, player_id="p1", recipients=["p1", "p2"])
    )
    spy_timers[0].start.assert_called_once_with("p1", ["p1", "p2"])
    spy_timers[1].start.assert_not_called()


def test_turn_timer_registry_cancels_turn_timer_on_turn_end(spy_timers, registry):
    registry.handle_turn_end(TurnEnded(room_id=1, player_id="p1"))
    spy_timers[0].cancel.assert_called_once_with("p1")
    spy_timers[1].cancel.assert_not_called()


@pytest.fixture
def event_scheduler_spy():
    return Mock(spec=EventScheduler)


@pytest.fixture
def turn_timer(event_scheduler_spy):
    return TurnTimer(
        event_scheduler=event_scheduler_spy,
        room_id=1,
        timeout_seconds=5,
        reminders_at_seconds_remaining=(1, 2),
    )


def test_turn_timer_schedules_alert_events_and_timeout_event(
    event_scheduler_spy, turn_timer
):
    turn_timer.start(player_id="p1", recipients=["p1", "p2"])
    assert event_scheduler_spy.schedule_event.call_count == 3
    assert event_scheduler_spy.schedule_event.call_args_list == [
        ((TurnTimeout(room_id=1, player_id="p1", recipients=["p1", "p2"]), 5),),
        (
            (
                TurnTimerAlert(
                    room_id=1,
                    player_id="p1",
                    seconds_remaining=1,
                    recipients=["p1", "p2"],
                ),
                4,
            ),
        ),
        (
            (
                TurnTimerAlert(
                    room_id=1,
                    player_id="p1",
                    seconds_remaining=2,
                    recipients=["p1", "p2"],
                ),
                3,
            ),
        ),
    ]


def test_turn_timer_allows_cancelling_player_scheduled_events(
    event_scheduler_spy, turn_timer
):
    turn_timer.start(player_id="p1", recipients=["p1", "p2"])
    turn_timer.start(player_id="p2", recipients=["p1", "p2"])
    turn_timer.cancel(player_id="p1")
    assert event_scheduler_spy.cancel_event.call_count == 3


def test_turn_timer_allows_cancelling_all_scheduled_events(
    event_scheduler_spy, turn_timer
):
    turn_timer.start(player_id="p1", recipients=["p1", "p2"])
    turn_timer.start(player_id="p2", recipients=["p1", "p2"])
    turn_timer.reset()
    assert event_scheduler_spy.cancel_event.call_count == 6
