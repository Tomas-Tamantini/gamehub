from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gamehub.api.routes.game_room import rooms_router
from gamehub.api.routes.socket import socket_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(socket_router)
app.include_router(rooms_router)
