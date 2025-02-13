import userService from "./user_service.js";

class SocketService {
    constructor(url, userService) {
        this.userService = userService;
        this.subscribers = [];
        this.ws = new WebSocket(url + "/ws?player_id=" + userService.getPlayerId());
        this.ws.onopen = () => {
            console.log("Connected to server");
        }
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.subscribers.forEach(callback => {
                callback(message);
            });
        }
    }

    send(data) {
        this.ws.send(JSON.stringify(data));
    }

    subscribe(callback) {
        this.subscribers.push(callback);
    }

    joinGame(game_type) {
        this.send({
            player_id: this.userService.getPlayerId(),
            request_type: "JOIN_GAME_BY_TYPE",
            payload: { game_type }
        });
    }

    makeMove(room_id, move) {
        this.send({
            player_id: this.userService.getPlayerId(),
            request_type: "MAKE_MOVE",
            payload: { room_id, move }
        });
    }
}

const playerId = prompt("Enter your player ID");
userService.setPlayerId(playerId);
export default new SocketService("ws://localhost:8000", userService);