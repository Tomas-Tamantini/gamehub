import { authBtn, playerIdSpan, joinGameBtn, statusArea, playerNames } from "./dom.js";

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

    if (state.players) {
        const offset = state.players.findIndex(player => player.player_id === state.playerId);
        state.players.forEach((player, i) => {
            const numPlayers = state.players.length;
            const domIdx = (i + numPlayers - offset) % numPlayers;
            playerNames[domIdx].textContent = `${player.player_id} - ${player.num_points} pts`
        });
    }
    else {
        playerNames.forEach(playerName => playerName.textContent = '');
    }
}