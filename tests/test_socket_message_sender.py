from unittest.mock import AsyncMock

import pytest

from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.message import Message, MessageType
from gamehub.socket_server import ClientManager, SocketMessageSender


@pytest.mark.asyncio
async def test_message_sender_does_not_send_message_if_client_not_found():
    client_manager = ClientManager()
    message_sender = SocketMessageSender(client_manager)
    msg = OutgoingMessage(
        player_id="Alice",
        message=Message(message_type=MessageType.GAME_STATE, payload={"key": "value"}),
    )
    await message_sender.send(msg)


@pytest.mark.asyncio
async def test_message_sender_sends_message_if_client_found():
    client_manager = ClientManager()
    client = AsyncMock()
    client_manager.associate_player_id("Alice", client)
    message_sender = SocketMessageSender(client_manager)
    msg = OutgoingMessage(
        player_id="Alice",
        message=Message(message_type=MessageType.GAME_STATE, payload={"key": "value"}),
    )
    await message_sender.send(msg)
    client.send_text.assert_called_once_with(
        '{"message_type":"GAME_STATE","payload":{"key":"value"}}'
    )
