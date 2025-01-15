import asyncio

import websockets

from gamehub.socket_server import ConnectionHandler


async def main():
    connection_handler = ConnectionHandler()
    server = await websockets.serve(connection_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
