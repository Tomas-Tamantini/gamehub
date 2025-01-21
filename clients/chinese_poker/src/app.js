import socket_service from "../../socket_service.js";
import { login, logout } from "./auth_service.js";
import { authBtn, joinGameBtn } from "./dom.js";
import state_store from "./state_store.js";

authBtn.addEventListener('click', () => {
    if (state_store.state.playerId) {
        state_store.action(logout)
    }
    else {
        const playerId = prompt('Enter your player id').trim();
        if (playerId)
            state_store.action(state => login(state, playerId));
    }
});

joinGameBtn.addEventListener('click', () => {
    socket_service.joinGame(state_store.state.playerId, 'chinese_poker');
});
