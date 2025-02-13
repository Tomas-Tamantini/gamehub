class UserService {
    constructor() {
        this.playerId = '';
    }

    setPlayerId(playerId) {
        this.playerId = playerId;
    }

    getPlayerId() {
        return this.playerId;
    }
}

export default new UserService();