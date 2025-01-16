import asyncio

import websockets

from gamehub.core.setup_bus import setup_event_bus
from gamehub.socket_server import ClientManager, ConnectionHandler, SocketMessageSender


async def main():
    client_manager = ClientManager()
    message_sender = SocketMessageSender(client_manager)
    event_bus = setup_event_bus(message_sender)
    connection_handler = ConnectionHandler(client_manager, event_bus)
    server = await websockets.serve(connection_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
