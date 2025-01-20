import asyncio

import websockets

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.room_manager import RoomManager
from gamehub.core.setup_bus import setup_event_bus
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
            )
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
