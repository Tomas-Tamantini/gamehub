import logging
from typing import Optional

from pydantic import ValidationError
from websockets import ConnectionClosed
from websockets.asyncio.server import ServerConnection

from gamehub.core.event_bus import EventBus
from gamehub.core.exceptions import DuplicatePlayerIdError
from gamehub.core.message import error_message
from gamehub.core.request import Request
from gamehub.socket_server.client_manager import ClientManager


class ConnectionHandler:
    def __init__(self, client_manager: ClientManager, event_bus: EventBus):
        self._client_manager = client_manager
        self._event_bus = event_bus

    @staticmethod
    async def _send_error_message(client: ServerConnection, payload: str) -> None:
        await client.send(error_message(payload).model_dump_json())

    @staticmethod
    async def _parse_request(
        client: ServerConnection, message: str
    ) -> Optional[Request]:
        try:
            return Request.model_validate_json(message)
        except ValidationError as e:
            error_msg = f"Unable to parse request: {e}"
            logging.debug(f"To {client.remote_address} - {error_msg}")
            await ConnectionHandler._send_error_message(client, error_msg)

    async def handle_client(self, client: ServerConnection) -> None:
        logging.info(f"Client connected: {client.remote_address}")
        try:
            async for message in client:
                if request := await self._parse_request(client, message):
                    try:
                        self._client_manager.associate_player_id(
                            request.player_id, client
                        )
                        await self._event_bus.publish(request)
                    except DuplicatePlayerIdError as e:
                        await ConnectionHandler._send_error_message(client, str(e))
        except ConnectionClosed:
            logging.warning(f"Client disconnected: {client.remote_address}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._client_manager.remove(client)
