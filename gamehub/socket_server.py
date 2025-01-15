import websockets

from gamehub.core.message import Message, MessageType


class SocketServer:
    async def handle_client(self, client: websockets.WebSocketServerProtocol):
        async for message in client:
            response = Message(
                message_type=MessageType.ERROR,
                payload=f"Unable to parse request: {message}",
            )
            await client.send(response.model_dump_json())
