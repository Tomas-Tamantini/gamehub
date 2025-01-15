import asyncio

import websockets

from gamehub.socket_server import SocketServer


async def main():
    socket_handler = SocketServer()
    server = await websockets.serve(socket_handler.handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
