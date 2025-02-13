from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from gamehub.api.dependencies import T_ConnectionHandler
from gamehub.api.routes.game_room import rooms_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, connection_handler: T_ConnectionHandler
):
    await connection_handler.handle_client(websocket)


app.include_router(rooms_router)
