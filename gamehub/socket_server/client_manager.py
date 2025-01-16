from typing import Optional

from websockets.asyncio.server import ServerConnection

from gamehub.core.exceptions import DuplicatePlayerIdError

# TODO:
# Handle two clients trying to connect with same player id
# Handle client disconnect


class ClientManager:
    def __init__(self):
        self._player_id_to_client = {}
        self._client_to_player_id = {}

    def associate_player_id(self, player_id: str, client: ServerConnection):
        existing_id = self._client_to_player_id.get(client)
        if not existing_id:
            self._player_id_to_client[player_id] = client
            self._client_to_player_id[client] = player_id
        elif existing_id != player_id:
            raise DuplicatePlayerIdError(
                f"Player ID '{player_id}' is already associated with another client"
            )

    def remove(self, client: ServerConnection):
        player_id = self._client_to_player_id.pop(client, None)
        if player_id:
            self._player_id_to_client.pop(player_id, None)

    def get_client(self, player_id: str) -> Optional[ServerConnection]:
        return self._player_id_to_client.get(player_id)
