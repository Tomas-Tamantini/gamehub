import gameContext from "../game_context.js";
import { statusArea } from "./dom.js";

var mySelection = "";

export default function handleMessage(msg) {
    if (msg.message_type == "ERROR") {
        statusArea.innerHTML = "ERROR: " + msg.payload.error;
    }
    else if (msg.message_type == "GAME_ROOM_UPDATE") {
        gameContext.roomId = msg.payload.room_id;
        statusArea.innerHTML = msg.payload.player_ids[0] + " joined the game";
    }
    else if (msg.message_type == "GAME_STATE") {
        if (msg.payload.private_view) {
            mySelection = msg.payload.private_view.selection;
            statusArea.innerHTML = "Your selection: " + mySelection;
        }
        else if (msg.payload.shared_view) {
            if (msg.payload.shared_view.result) {
                mySelection = "";
                if (msg.payload.shared_view.result.winner) {
                    statusArea.innerHTML = msg.payload.shared_view.result.winner + " wins!";
                }
                else {
                    statusArea.innerHTML = "It's a tie!";
                }
            }
            else {
                if (mySelection) {
                    statusArea.innerHTML = "Waiting for other players to make their move";
                }
                else {
                    statusArea.innerHTML = "Make your move";
                }
            }
        }
    }
    else {
        statusArea.innerHTML = msg;
    }
}