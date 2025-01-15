from typing import Optional

import websockets


class ClientManager:
    def __init__(self):
        self._player_id_to_client = {}

    def associate_player_id(
        self, player_id: str, client: websockets.WebSocketServerProtocol
    ):
        self._player_id_to_client[player_id] = client

    def get_client(
        self, player_id: str
    ) -> Optional[websockets.WebSocketServerProtocol]:
        return self._player_id_to_client.get(player_id)
