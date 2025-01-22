import { authBtn, playerIdSpan, joinGameBtn, statusArea, playerNames, opponentCards } from "./dom.js";

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
            if (domIdx > 0) {
                opponentCards[domIdx - 1].style.display = 'flex';
                opponentCards[domIdx - 1].textContent = `x${player.num_cards}`;
            }
        });
    }
    else {
        playerNames.forEach(playerName => playerName.textContent = '');
        opponentCards.forEach(opponentCard => {
            opponentCard.textContent = '';
            opponentCard.style.display = 'none';
        });
    }
}