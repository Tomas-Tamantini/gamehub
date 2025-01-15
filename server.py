import asyncio

import websockets

from gamehub.socket_server import ClientManager, ConnectionHandler


async def main():
    client_manager = ClientManager()
    connection_handler = ConnectionHandler(client_manager)
    server = await websockets.serve(connection_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
