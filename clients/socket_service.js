class SocketService {
    constructor(url) {
        this.subscribers = [];
        this.ws = new WebSocket(url);
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
}


export default new SocketService("ws://localhost:8765");