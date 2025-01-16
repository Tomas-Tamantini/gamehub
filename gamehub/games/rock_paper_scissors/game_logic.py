from gamehub.games.rock_paper_scissors.game_state import RPSGameState, RPSPlayer
from gamehub.games.rock_paper_scissors.move import RPSMove


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

    @staticmethod
    def make_move(state: RPSGameState, move: RPSMove) -> RPSGameState:
        new_players = []
        for player in state.players:
            if player.player_id == move.player_id:
                new_players.append(
                    RPSPlayer(player_id=player.player_id, selection=move.selection)
                )
            else:
                new_players.append(player)
        return RPSGameState(players=new_players)
