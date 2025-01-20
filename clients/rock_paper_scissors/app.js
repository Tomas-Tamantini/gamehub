import socketService from "../socket_service.js";
import {
    startGameBtn,
    rockBtn,
    paperBtn,
    scissorsBtn
} from "./dom.js";
import handleMessage from "./handle_message.js";
import { joinGame, makeMove } from "./requests.js";


socketService.subscribe(handleMessage)
startGameBtn.onclick = joinGame;
rockBtn.onclick = () => makeMove("ROCK");
paperBtn.onclick = () => makeMove("PAPER");
scissorsBtn.onclick = () => makeMove("SCISSORS");


