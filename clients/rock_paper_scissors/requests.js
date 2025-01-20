import player_id from "./user_service.js";
import socketService from "../socket_service.js";


export function joinGame() {
    socketService.send({
        player_id: player_id(),
        request_type: "JOIN_GAME",
        payload: { room_id: 1 }
    });
}

export function makeMove(move) {
    socketService.send({
        player_id: player_id(),
        request_type: "MAKE_MOVE",
        payload: { room_id: 1, move: { selection: move } }
    });
}