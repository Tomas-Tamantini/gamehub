from typing import Optional

from fastapi import WebSocket

from gamehub.core.exceptions import AmbiguousPlayerIdError


class ClientManager:
    def __init__(self):
        self._player_id_to_client = {}
        self._client_to_player_id = {}

    def associate_player_id(self, player_id: str, client: WebSocket):
        existing_id = self._client_to_player_id.get(client)
        if not existing_id:
            existing_client = self._player_id_to_client.get(player_id)
            if existing_client:
                raise AmbiguousPlayerIdError(
                    "Player id already in use by another client"
                )
            else:
                self._player_id_to_client[player_id] = client
                self._client_to_player_id[client] = player_id
        elif existing_id != player_id:
            raise AmbiguousPlayerIdError(
                "This client is already associated with another id"
            )

    def remove(self, client: WebSocket) -> Optional[str]:
        player_id = self._client_to_player_id.pop(client, None)
        if player_id:
            self._player_id_to_client.pop(player_id, None)
            return player_id

    def get_client(self, player_id: str) -> Optional[WebSocket]:
        return self._player_id_to_client.get(player_id)
