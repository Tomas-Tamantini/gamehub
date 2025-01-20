import socketService from "../socket_service.js";
import {
    nameInput,
    startGameBtn,
    rockBtn,
    paperBtn,
    scissorsBtn,
    statusArea
} from "./dom.js";


var mySelection = "";

function player_id() {
    return nameInput.value;
}

socketService.subscribe(
    msg => {
        if (msg.message_type == "ERROR") {
            statusArea.innerHTML = "ERROR: " + msg.payload.error;
        }
        else if (msg.message_type == "PLAYER_JOINED") {
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
            statusArea.innerHTML = event.data;
        }
    }
)

startGameBtn.onclick = function () {
    socketService.send({
        player_id: player_id(),
        request_type: "JOIN_GAME",
        payload: { room_id: 1 }

    });
}

function makeMove(move) {
    socketService.send({
        player_id: player_id(),
        request_type: "MAKE_MOVE",
        payload: { room_id: 1, move: { selection: move } }
    });
}

rockBtn.onclick = () => makeMove("ROCK");
paperBtn.onclick = () => makeMove("PAPER");
scissorsBtn.onclick = () => makeMove("SCISSORS");


