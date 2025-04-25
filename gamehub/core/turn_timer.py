import asyncio
from typing import Iterable, Optional

from gamehub.core.event_bus import EventBus
from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)
from gamehub.core.events.timer_events import TurnTimeout, TurnTimerAlert


class TurnTimer:
    def __init__(
        self,
        event_bus: EventBus,
        room_id: int,
        timeout_seconds: int,
        reminders_at_seconds_remaining: Iterable[int],
    ) -> None:
        self._room_id = room_id
        self._event_bus = event_bus
        self._timeout_seconds = timeout_seconds
        self._reminders_at_seconds_remaining = set(reminders_at_seconds_remaining)

    @property
    def room_id(self) -> int:
        return self._room_id

    def reset(self) -> None: ...  # TODO: Implement reset logic

    async def start(self, player_id: str) -> None:
        async def schedule_event(
            event: TurnTimerAlert | TurnTimeout, wait_seconds: int
        ) -> None:
            await asyncio.sleep(wait_seconds)
            await self._event_bus.publish(event)

        asyncio.create_task(
            schedule_event(
                TurnTimeout(room_id=self._room_id, player_id=player_id),
                self._timeout_seconds,
            )
        )
        for seconds_remaining in self._reminders_at_seconds_remaining:
            event = TurnTimerAlert(
                room_id=self._room_id,
                player_id=player_id,
                time_left_seconds=seconds_remaining,
            )
            schedule_time = self._timeout_seconds - seconds_remaining
            asyncio.create_task(schedule_event(event, schedule_time))

    def cancel(self, player_id: str) -> None: ...  # TODO: Implement timer cancel logic


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

    async def handle_turn_start(self, turn_start_event: TurnStarted):
        if timer := self._turn_timer(turn_start_event.room_id):
            await timer.start(turn_start_event.player_id)

    def handle_turn_end(self, turn_end_event: TurnEnded):
        if timer := self._turn_timer(turn_end_event.room_id):
            timer.cancel(turn_end_event.player_id)
