import player_id from "./user_service.js";
import socketService from "../socket_service.js";

const room_id = 1;

export function joinGame() {
    socketService.joinGame(player_id(), room_id);
}

export function makeMove(cell_index) {
    socketService.makeMove(player_id(), room_id, { cell_index });
}