import {
    authBtn,
    playerIdSpan,
    joinGameBtn,
    statusArea,
    playerNames,
    opponentCards,
    myCardsContainer,
    dealer,
    makeMoveBtn
} from "./dom.js";

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
                opponentCards[domIdx - 1].textContent = player.num_cards;
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

    if (state.myCards) {
        myCardsContainer.innerHTML = '';
        const suitSymbols = { 'd': '♦', 'c': '♣', 'h': '♥', 's': '♠' };
        state.myCards.forEach((card, index) => {
            const cardDiv = document.createElement('div');
            cardDiv.classList.add('card');
            cardDiv.classList.add('my-card');
            if (card.suit === 'd' || card.suit === 'h') {
                cardDiv.classList.add('red');
            }
            else {
                cardDiv.classList.add('black');
            }
            cardDiv.dataset.index = index;
            const cardText = document.createTextNode(`${card.rank}${suitSymbols[card.suit]}`);
            cardDiv.appendChild(cardText);
            cardDiv.addEventListener('click', () => {
                cardDiv.classList.toggle('selected');
            });
            myCardsContainer.appendChild(cardDiv);
        })
    }
    else {
        myCardsContainer.innerHTML = '';
    }

    if (state.currentPlayerId) {
        const myIdx = state.players.findIndex(player => player.player_id === state.playerId);
        const dealerIdx = state.players.findIndex(player => player.player_id === state.currentPlayerId);
        const offset = (dealerIdx - myIdx + state.players.length) % state.players.length;
        dealer.style.display = 'flex';
        if (offset == 0) {
            dealer.style.bottom = '20%';
            dealer.style.left = '50%';
            dealer.style.transform = 'translateX(-50%)';
            makeMoveBtn.style.display = 'flex';
        }
        else if (offset == 1) {
            dealer.style.bottom = '50%';
            dealer.style.left = '25%';
            dealer.style.transform = 'translateY(50%)';
            makeMoveBtn.style.display = 'none';
        }
        else if (offset == 2) {
            dealer.style.top = '25%';
            dealer.style.left = '50%';
            dealer.style.transform = 'translateX(-50%)';
            makeMoveBtn.style.display = 'none';
        }
        else {
            dealer.style.bottom = '50%';
            dealer.style.right = '25%';
            dealer.style.transform = 'translateY(50%)';
            makeMoveBtn.style.display = 'none';
        }
    }
    else {
        dealer.style.display = 'none';
        makeMoveBtn.style.display = 'none';
    }
}