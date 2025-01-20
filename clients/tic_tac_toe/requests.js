import player_id from "./user_service.js";
import socketService from "../socket_service.js";
import gameContext from "../game_context.js";


export function joinGame() {
    socketService.joinGame(player_id(), 'tic_tac_toe');
}

export function makeMove(cell_index) {
    socketService.makeMove(player_id(), gameContext.roomId, { cell_index });
}