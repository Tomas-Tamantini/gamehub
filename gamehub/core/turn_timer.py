import asyncio
from collections import defaultdict
from typing import Iterable, Optional

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)
from gamehub.core.events.timer_events import TurnTimeout, TurnTimerAlert


class EventScheduler:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    def schedule_event(self, event: any, wait_seconds: int) -> asyncio.Task:
        async def schedule_event():
            await asyncio.sleep(wait_seconds)
            await self._event_bus.publish(event)

        return asyncio.create_task(schedule_event())

    @staticmethod
    def cancel_event(task: asyncio.Task) -> None:
        if not task.done():
            task.cancel()


class TurnTimer:
    def __init__(
        self,
        event_scheduler: EventScheduler,
        room_id: int,
        timeout_seconds: int,
        reminders_at_seconds_remaining: Iterable[int],
    ) -> None:
        self._scheduler = event_scheduler
        self._room_id = room_id
        self._timeout_seconds = timeout_seconds
        self._reminders_at_seconds_remaining = set(reminders_at_seconds_remaining)
        self._scheduled_tasks = defaultdict(list)

    @property
    def room_id(self) -> int:
        return self._room_id

    def reset(self) -> None:
        for player_id in self._scheduled_tasks:
            self.cancel(player_id)
        self._scheduled_tasks.clear()

    def _schedule_event(self, event: any, delay_seconds: int) -> None:
        task = self._scheduler.schedule_event(event, delay_seconds)
        self._scheduled_tasks[event.player_id].append(task)

    def start(self, player_id: str) -> None:
        self.cancel(player_id)

        timeout_event = TurnTimeout(room_id=self._room_id, player_id=player_id)
        self._schedule_event(timeout_event, self._timeout_seconds)
        for seconds_remaining in self._reminders_at_seconds_remaining:
            event = TurnTimerAlert(
                room_id=self._room_id,
                player_id=player_id,
                time_left_seconds=seconds_remaining,
            )
            delay = self._timeout_seconds - seconds_remaining
            self._schedule_event(event, delay)

    def cancel(self, player_id: str) -> None:
        for task in self._scheduled_tasks[player_id]:
            self._scheduler.cancel_event(task)
        self._scheduled_tasks[player_id].clear()


class TurnTimerRegistry:
    def __init__(self, turn_timers: Iterable[TurnTimer]) -> None:
        self._turn_timers = {t.room_id: t for t in turn_timers}

    def _turn_timer(self, room_id: int) -> Optional[TurnTimer]:
        return self._turn_timers.get(room_id)

    def handle_game_start(self, game_start_event: GameStarted):
        if timer := self._turn_timer(game_start_event.room_id):
            timer.reset()

    def handle_game_end(self, game_end_event: GameEnded):
        if timer := self._turn_timer(game_end_event.room_id):
            timer.reset()

    def handle_turn_start(self, turn_start_event: TurnStarted):
        if timer := self._turn_timer(turn_start_event.room_id):
            timer.start(turn_start_event.player_id)

    def handle_turn_end(self, turn_end_event: TurnEnded):
        if timer := self._turn_timer(turn_end_event.room_id):
            timer.cancel(turn_end_event.player_id)
