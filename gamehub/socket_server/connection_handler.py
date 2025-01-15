from typing import Optional

import websockets
from pydantic import ValidationError

from gamehub.core.message import Message, MessageType
from gamehub.core.request import Request
from gamehub.socket_server.client_manager import ClientManager


class ConnectionHandler:
    def __init__(self, client_manager: ClientManager):
        self._client_manager = client_manager

    @staticmethod
    async def _parse_request(
        client: websockets.WebSocketServerProtocol, message: str
    ) -> Optional[Request]:
        try:
            return Request.model_validate_json(message)
        except ValidationError as e:
            response = Message(
                message_type=MessageType.ERROR,
                payload=f"Unable to parse request: {e}",
            )
            await client.send(response.model_dump_json())

    async def handle_client(self, client: websockets.WebSocketServerProtocol) -> None:
        async for message in client:
            if request := await self._parse_request(client, message):
                self._client_manager.associate_player_id(request.player_id, client)
