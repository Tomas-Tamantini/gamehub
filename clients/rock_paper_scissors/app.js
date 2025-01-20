import socketService from "../socket_service.js";
import {
    startGameBtn,
    rockBtn,
    paperBtn,
    scissorsBtn
} from "./dom.js";
import handleMessage from "./handle_message.js";
import { joinGame, selectMove } from "./requests.js";


socketService.subscribe(handleMessage)
startGameBtn.onclick = joinGame;
rockBtn.onclick = () => selectMove("ROCK");
paperBtn.onclick = () => selectMove("PAPER");
scissorsBtn.onclick = () => selectMove("SCISSORS");


