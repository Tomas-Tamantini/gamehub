import { authBtn, playerIdSpan } from "./dom.js";

export default function updateDom(state) {
    if (state.playerId) {
        playerIdSpan.textContent = state.playerId;
        authBtn.textContent = 'Logout';
    }
    else {
        playerIdSpan.textContent = '';
        authBtn.textContent = 'Login';
    }
}