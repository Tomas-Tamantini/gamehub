import asyncio

import websockets

from gamehub.core.event_bus import EventBus
from gamehub.core.game_room import GameRoom
from gamehub.core.message import MessageEvent
from gamehub.core.request import Request
from gamehub.core.room_manager import RoomManager
from gamehub.games.rock_paper_scissors import RPSGameLogic, RPSMove
from gamehub.socket_server import ClientManager, ConnectionHandler, SocketMessageSender


async def main():
    event_bus = EventBus()
    client_manager = ClientManager()
    message_sender = SocketMessageSender(client_manager)
    game_room = GameRoom(
        room_id=1,
        game_logic=RPSGameLogic(),
        move_parser=RPSMove.model_validate,
        event_bus=event_bus,
    )
    room_manager = RoomManager([game_room], event_bus)
    event_bus.subscribe(Request, room_manager.handle_request)

    event_bus.subscribe(MessageEvent, message_sender.send)
    connection_handler = ConnectionHandler(client_manager, event_bus)
    server = await websockets.serve(connection_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
