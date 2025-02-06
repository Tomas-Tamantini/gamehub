from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from gamehub.api.dependencies.client_manager import T_ClientManager
from gamehub.api.socket_server import SocketMessageSender
from gamehub.core.message_sender import MessageSender


@lru_cache
def get_message_sender(client_manager: T_ClientManager) -> MessageSender:
    return SocketMessageSender(client_manager)


T_MessageSender = Annotated[MessageSender, Depends(get_message_sender)]
