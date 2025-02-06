from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.api.socket_server import ClientManager


@lru_cache
def get_client_manager() -> ClientManager:
    return ClientManager()


T_ClientManager = Annotated[ClientManager, Depends(get_client_manager)]
