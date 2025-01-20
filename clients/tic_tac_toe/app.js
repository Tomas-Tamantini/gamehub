import handleMessage from "./handle_message.js";
import socket_service from "../socket_service.js";
import { gridCells, resetGridCells, startGameBtn } from "./dom.js";
import { joinGame, makeMove } from "./requests.js";

socket_service.subscribe(handleMessage);
startGameBtn.onclick = () => {
    resetGridCells();
    joinGame();
}

gridCells.forEach((cell) => {
    cell.addEventListener('click', () => {
        const cellIndex = cell.getAttribute('data-cell');
        makeMove(cellIndex);
    });
});