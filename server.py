import asyncio

import websockets

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.room_manager import RoomManager
from gamehub.core.setup_bus import setup_event_bus
from gamehub.games.chinese_poker import (
    ChinesePokerConfiguration,
    ChinesePokerGameLogic,
    ChinesePokerMove,
)
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from gamehub.games.tic_tac_toe import TicTacToeGameLogic, TicTacToeMove
from gamehub.socket_server import ClientManager, ConnectionHandler, SocketMessageSender


def game_manager(event_bus: EventBus) -> RoomManager:
    return RoomManager(
        rooms=[
            GameRoom(
                room_id=1,
                game_logic=TicTacToeGameLogic(),
                move_parser=TicTacToeMove.model_validate,
                event_bus=event_bus,
            ),
            GameRoom(
                room_id=2,
                game_logic=RPSGameLogic(),
                move_parser=RPSMove.model_validate,
                event_bus=event_bus,
            ),
            GameRoom(
                room_id=3,
                game_logic=ChinesePokerGameLogic(
                    ChinesePokerConfiguration(
                        num_players=4, cards_per_player=13, game_over_point_threshold=30
                    )
                ),
                move_parser=ChinesePokerMove.model_validate,
                event_bus=event_bus,
            ),
            GameRoom(
                room_id=4,
                game_logic=ChinesePokerGameLogic(
                    ChinesePokerConfiguration(
                        num_players=4, cards_per_player=13, game_over_point_threshold=30
                    )
                ),
                move_parser=ChinesePokerMove.model_validate,
                event_bus=event_bus,
            ),
        ],
        event_bus=event_bus,
    )


async def main():
    event_bus = EventBus()
    client_manager = ClientManager()
    message_sender = SocketMessageSender(client_manager)
    setup_event_bus(event_bus, message_sender, game_manager(event_bus))
    connection_handler = ConnectionHandler(client_manager, event_bus)
    server = await websockets.serve(connection_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
