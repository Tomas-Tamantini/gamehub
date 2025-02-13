import logging
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from gamehub.api.socket_server.client_manager import ClientManager
from gamehub.core.event_bus import EventBus
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.request import Request
from gamehub.core.exceptions import InvalidPlayerIdError
from gamehub.core.message import error_message


class ConnectionHandler:
    def __init__(self, client_manager: ClientManager, event_bus: EventBus):
        self._client_manager = client_manager
        self._event_bus = event_bus

    @staticmethod
    async def _send_error_message(client: WebSocket, payload: str) -> None:
        await client.send_text(error_message(payload).model_dump_json())

    @staticmethod
    async def _parse_request(client: WebSocket, message: str) -> Optional[Request]:
        try:
            return Request.model_validate_json(message)
        except ValidationError as e:
            error_msg = f"Unable to parse request: {e}"
            await ConnectionHandler._send_error_message(client, error_msg)

    async def handle_client(self, client: WebSocket, player_id: str) -> None:
        # TODO: Remove player id from request class
        try:
            await client.accept()
            while True:
                message = await client.receive_text()
                if request := await self._parse_request(client, message):
                    try:
                        self._client_manager.associate_player_id(
                            request.player_id, client
                        )
                        await self._event_bus.publish(request)
                    except InvalidPlayerIdError as e:
                        await ConnectionHandler._send_error_message(client, str(e))
        except WebSocketDisconnect:
            logging.warning(f"Client disconnected: {client.url}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            if player_id := self._client_manager.remove(client):
                await self._event_bus.publish(PlayerDisconnected(player_id))
