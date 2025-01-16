from gamehub.games.rock_paper_scissors.game_state import RPSGameState, RPSPlayer


class RPSGameLogic:
    @property
    def num_players(self) -> int:
        return 2

    @staticmethod
    def initial_state(*player_ids: str) -> RPSGameState:
        return RPSGameState(
            players=[
                RPSPlayer(player_id=player_id, selection=None)
                for player_id in player_ids
            ]
        )
