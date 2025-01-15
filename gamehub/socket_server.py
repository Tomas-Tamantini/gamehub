import websockets


class SocketServer:
    async def handle_client(self, client: websockets.WebSocketServerProtocol):
        async for message in client:
            await client.send(f"Unable to parse request: {message}")
