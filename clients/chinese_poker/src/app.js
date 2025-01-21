import { login, logout } from "./auth_service.js";
import { authBtn } from "./dom.js";
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