const serverUrl = "ws://localhost:8765";
const nameInput = document.getElementById("name");
const startGameBtn = document.getElementById("start-game");
const rockBtn = document.getElementById("rock");
const paperBtn = document.getElementById("paper");
const scissorsBtn = document.getElementById("scissors");
const statusArea = document.getElementById("status");

const ws = new WebSocket(serverUrl);
var mySelection = "";

function player_id() {
    return nameInput.value;
}

ws.onopen = function () {
    statusArea.innerHTML = "Connected to server";
}

ws.onmessage = function (event) {
    const message = JSON.parse(event.data);
    if (message.message_type == "ERROR") {
        statusArea.innerHTML = "ERROR: " + message.payload.error;
    }
    else if (message.message_type == "PLAYER_JOINED") {
        statusArea.innerHTML = message.payload.player_ids[0] + " joined the game";
    }
    else if (message.message_type == "GAME_STATE") {
        if (message.payload.private_view) {
            mySelection = message.payload.private_view.selection;
            statusArea.innerHTML = "Your selection: " + mySelection;
        }
        else if (message.payload.shared_view) {
            if (message.payload.shared_view.result) {
                mySelection = "";
                if (message.payload.shared_view.result.winner) {
                    statusArea.innerHTML = message.payload.shared_view.result.winner + " wins!";
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

startGameBtn.onclick = function () {
    ws.send(JSON.stringify({
        player_id: player_id(),
        request_type: "JOIN_GAME",
        payload: { room_id: 1 }

    }));
}

function makeMove(move) {
    ws.send(JSON.stringify({
        player_id: player_id(),
        request_type: "MAKE_MOVE",
        payload: { room_id: 1, move: { selection: move } }
    }));
}

rockBtn.onclick = () => makeMove("ROCK");
paperBtn.onclick = () => makeMove("PAPER");
scissorsBtn.onclick = () => makeMove("SCISSORS");


