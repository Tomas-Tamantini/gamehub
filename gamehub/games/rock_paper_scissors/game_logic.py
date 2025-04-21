from typing import Iterator

from gamehub.games.rock_paper_scissors.game_state import RPSGameState, RPSPlayer
from gamehub.games.rock_paper_scissors.move import RPSMove


class RPSGameLogic:
    @property
    def num_players(self) -> int:
        return 2

    @property
    def game_type(self) -> str:
        return "rock_paper_scissors"

    @property
    def configuration(self):
        return None

    @staticmethod
    def initial_state(*player_ids: str) -> RPSGameState:
        return RPSGameState(
            players=[
                RPSPlayer(player_id=player_id, selection=None)
                for player_id in player_ids
            ]
        )

    @staticmethod
    def next_automated_state(state: RPSGameState):
        return None

    @staticmethod
    def make_move(state: RPSGameState, move: RPSMove) -> RPSGameState:
        new_players = []
        for player in state.players:
            if player.player_id == move.player_id:
                new_players.append(player.make_selection(move.selection))
            else:
                new_players.append(player)
        return RPSGameState(players=new_players)

    @staticmethod
    def derived_events(state: RPSGameState, room_id: int) -> Iterator[object]:
        return iter([])
