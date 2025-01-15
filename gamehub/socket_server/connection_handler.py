import logging
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
            error_msg = f"Unable to parse request: {e}"
            logging.debug(f"To {client.remote_address} - {error_msg}")
            response = Message(message_type=MessageType.ERROR, payload=error_msg)
            await client.send(response.model_dump_json())

    async def handle_client(self, client: websockets.WebSocketServerProtocol) -> None:
        logging.info(f"Client connected: {client.remote_address}")
        try:
            async for message in client:
                if request := await self._parse_request(client, message):
                    self._client_manager.associate_player_id(request.player_id, client)
        except websockets.ConnectionClosed:
            logging.warning(f"Client disconnected: {client.remote_address}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._client_manager.remove(client)
