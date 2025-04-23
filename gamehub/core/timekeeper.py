from gamehub.core.events.game_state_update import (
    GameEnded,
    GameStarted,
    TurnEnded,
    TurnStarted,
)


class Timekeeper:
    def handle_game_start(
        self, game_start_event: GameStarted
    ): ...  # TODO: Implement game start logic

    def handle_game_end(
        self, game_end_event: GameEnded
    ): ...  # TODO: Implement game end logic

    def handle_turn_start(
        self, turn_start_event: TurnStarted
    ): ...  # TODO: Implement turn start logic

    def handle_turn_end(
        self, turn_end_event: TurnEnded
    ): ...  # TODO: Implement turn end logic
