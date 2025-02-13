import socketService from "../socket_service.js";
import gameContext from "../game_context.js";


export function joinGame() {
    socketService.joinGame('tic_tac_toe');
}

export function makeMove(cell_index) {
    socketService.makeMove(gameContext.roomId, { cell_index });
}