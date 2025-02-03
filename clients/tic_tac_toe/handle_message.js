import gameContext from "../game_context.js";
import { statusArea, gridCells } from "./dom.js";
import player_id from "./user_service.js";

function statusMsg(view) {
    if (view.is_over) {
        if (view.winner) return view.winner + " wins!";
        else return "It's a tie!";
    }
    else {
        if (player_id() == view.current_player) return "Make your move";
        else return `Waiting for ${view.current_player} to make their move`;
    }
}

export default function handleMessage(msg) {
    if (msg.message_type == "ERROR") {
        statusArea.innerHTML = "ERROR: " + msg.payload.error;
    }
    else if (msg.message_type == "GAME_ROOM_UPDATE") {
        gameContext.roomId = msg.payload.room_id;
        statusArea.innerHTML = msg.payload.player_ids[0] + " joined the game";
    }
    else if (msg.message_type == "GAME_STATE") {
        const view = msg.payload.shared_view;
        statusArea.innerHTML = statusMsg(view);
        const symbols = ["X", "O"];
        view.players.forEach((player, playerIdx) => {
            const symbol = symbols[playerIdx];
            player.selections.forEach(cellIdx => {
                gridCells[cellIdx].innerHTML = symbol;
            });
        });
    }
    else {
        statusArea.innerHTML = msg;
    }
}