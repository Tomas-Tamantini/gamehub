from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.socket_server.client_manager import ClientManager


class SocketMessageSender:
    def __init__(self, client_manager: ClientManager):
        self._client_manager = client_manager

    async def send(self, message_event: OutgoingMessage) -> None:
        if client := self._client_manager.get_client(message_event.player_id):
            await client.send_text(message_event.message.model_dump_json())
