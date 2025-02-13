import socketService from "../socket_service.js";
import gameContext from "../game_context.js";

export function joinGame() {
    socketService.joinGame('rock_paper_scissors');
}

export function selectMove(selection) {
    socketService.makeMove(gameContext.roomId, { selection });
}