from fastapi import FastAPI, WebSocket

from gamehub.api.dependencies import T_ConnectionHandler

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, connection_handler: T_ConnectionHandler
):
    await connection_handler.handle_client(websocket)
