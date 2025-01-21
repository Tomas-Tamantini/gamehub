import { authBtn, playerIdSpan, joinGameBtn, statusArea } from "./dom.js";

export default function updateDom(state) {
    if (state.playerId) {
        playerIdSpan.textContent = state.playerId;
        authBtn.textContent = 'Logout';
        joinGameBtn.disabled = false;
    }
    else {
        playerIdSpan.textContent = '';
        authBtn.textContent = 'Login';
        joinGameBtn.disabled = true;
    }
    if (state.statusMsg) {
        statusArea.textContent = state.statusMsg;
    }
    else {
        statusArea.textContent = '';
    }
}