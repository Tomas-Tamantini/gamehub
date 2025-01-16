from gamehub.core.game_setup import GameSetup
from gamehub.games.rock_paper_scissors.game_state import RPSGameState, RPSPlayer


def _initial_state(player_ids: list[str]) -> RPSGameState:
    return RPSGameState(
        players=[
            RPSPlayer(player_id=player_id, selection=None) for player_id in player_ids
        ]
    )


def rps_setup() -> GameSetup:
    return GameSetup(
        num_players=2,
        initial_state=_initial_state,
    )
