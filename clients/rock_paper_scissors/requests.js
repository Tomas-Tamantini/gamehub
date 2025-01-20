import player_id from "./user_service.js";
import socketService from "../socket_service.js";
import gameContext from "../game_context.js";

export function joinGame() {
    socketService.joinGame(player_id(), 'rock_paper_scissors');
}

export function selectMove(selection) {
    socketService.makeMove(player_id(), gameContext.roomId, { selection });
}