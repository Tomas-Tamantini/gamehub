import handleMessage from "./handle_message.js";
import socket_service from "../socket_service.js";
import { startGameBtn } from "./dom.js";
import { joinGame } from "./requests.js";

socket_service.subscribe(handleMessage);
startGameBtn.onclick = joinGame;