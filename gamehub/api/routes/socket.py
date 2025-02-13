from fastapi import APIRouter, WebSocket

from gamehub.api.dependencies import T_ConnectionHandler

socket_router = APIRouter(prefix="/ws", tags=["websocket"])


@socket_router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, connection_handler: T_ConnectionHandler
):
    await connection_handler.handle_client(websocket)
