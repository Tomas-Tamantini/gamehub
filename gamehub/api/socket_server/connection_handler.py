import logging
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from gamehub.api.socket_server.client_manager import ClientManager
from gamehub.core.event_bus import EventBus
from gamehub.core.events.player_disconnected import PlayerDisconnected
from gamehub.core.events.socket_request import SocketRequest
from gamehub.core.exceptions import InvalidPlayerIdError
from gamehub.core.message import error_message


class ConnectionHandler:
    def __init__(self, client_manager: ClientManager, event_bus: EventBus):
        self._client_manager = client_manager
        self._event_bus = event_bus

    @staticmethod
    async def _send_error_message(client: WebSocket, payload: str) -> None:
        await client.send_text(error_message(payload).model_dump_json())

    async def _listen_to_messages(self, client: WebSocket, player_id: str) -> None:
        while True:
            message = await client.receive_text()
            request = SocketRequest(player_id=player_id, raw_request=message)
            await self._event_bus.publish(request)

    async def handle_client(self, client: WebSocket, player_id: str) -> None:
        try:
            await client.accept()
            try:
                self._client_manager.associate_player_id(player_id, client)
                await self._listen_to_messages(client, player_id)
            except InvalidPlayerIdError as e:
                await ConnectionHandler._send_error_message(client, str(e))
                await client.close()

        except WebSocketDisconnect:
            logging.warning(f"Client disconnected: {client.url}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            if player_id := self._client_manager.remove(client):
                await self._event_bus.publish(PlayerDisconnected(player_id))
