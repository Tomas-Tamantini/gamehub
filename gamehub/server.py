from http import HTTPStatus

from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gamehub.api.dependencies import T_ConnectionHandler, T_RoomManager
from gamehub.core.room_state import RoomState

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


class GetRoomsQueryParameters(BaseModel):
    game_type: str = None


class GetRoomsResponse(BaseModel):
    items: list[RoomState]


@app.get("/rooms", status_code=HTTPStatus.OK, response_model=GetRoomsResponse)
async def get_rooms(
    room_manager: T_RoomManager, query_parameters: GetRoomsQueryParameters = Depends()
):
    rooms = list(room_manager.room_states(query_parameters.game_type))
    return GetRoomsResponse(items=rooms)
