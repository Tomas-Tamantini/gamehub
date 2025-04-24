from typing import Iterable, Optional

from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)


class TurnTimer:
    def __init__(self, room_id: int) -> None:
        self._room_id = room_id

    @property
    def room_id(self) -> int:
        return self._room_id

    def reset(self) -> None: ...  # TODO: Implement reset logic

    def start(self, player_id: str) -> None: ...  # TODO: Implement timer start logic

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

    def handle_turn_start(self, turn_start_event: TurnStarted):
        if timer := self._turn_timer(turn_start_event.room_id):
            timer.start(turn_start_event.player_id)

    def handle_turn_end(self, turn_end_event: TurnEnded):
        if timer := self._turn_timer(turn_end_event.room_id):
            timer.cancel(turn_end_event.player_id)
