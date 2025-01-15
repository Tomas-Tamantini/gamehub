from typing import Optional

import websockets


class ClientManager:
    def __init__(self):
        self._player_id_to_client = {}
        self._client_to_player_id = {}

    def associate_player_id(
        self, player_id: str, client: websockets.WebSocketServerProtocol
    ):
        self._player_id_to_client[player_id] = client
        self._client_to_player_id[client] = player_id

    def remove(self, client: websockets.WebSocketServerProtocol):
        player_id = self._client_to_player_id.pop(client, None)
        if player_id:
            self._player_id_to_client.pop(player_id, None)

    def get_client(
        self, player_id: str
    ) -> Optional[websockets.WebSocketServerProtocol]:
        return self._player_id_to_client.get(player_id)
