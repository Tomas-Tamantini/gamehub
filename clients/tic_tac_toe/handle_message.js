import { statusArea } from "./dom.js";


export default function handleMessage(msg) {
    if (msg.message_type == "ERROR") {
        statusArea.innerHTML = "ERROR: " + msg.payload.error;
    }
    else if (msg.message_type == "PLAYER_JOINED") {
        statusArea.innerHTML = msg.payload.player_ids[0] + " joined the game";
    }
    else if (msg.message_type == "GAME_STATE") {

    }
    else {
        statusArea.innerHTML = msg;
    }
}