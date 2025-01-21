import { authBtn, playerIdSpan } from "./dom.js";


class UserService {
    constructor() {
        this.updateDom();
    }

    isLoggedIn() {
        return this.getPlayerId();
    }

    updateDom() {
        if (this.isLoggedIn()) {
            playerIdSpan.textContent = this.getPlayerId();
            authBtn.textContent = 'Logout';
        }
        else {
            playerIdSpan.textContent = '';
            authBtn.textContent = 'Login';
        }
    }

    getPlayerId() {
        return localStorage.getItem('ghPlayerId');
    }

    login(playerId) {
        const trimmed = playerId?.trim();
        if (trimmed) {
            localStorage.setItem('ghPlayerId', trimmed);
            this.updateDom();
        }
    }

    logout() {
        localStorage.removeItem('ghPlayerId');
        this.updateDom();
    }
}

export default new UserService();