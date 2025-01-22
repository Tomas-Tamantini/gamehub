export const authBtn = document.getElementById('auth-button');
export const playerIdSpan = document.getElementById('player-id');
export const joinGameBtn = document.getElementById('join-button');
export const statusArea = document.getElementById('status');
export const playerNames = Array.from({ length: 4 }, (_, i) =>
    document.getElementById(`player-name-${i}`)
);
export const opponentCards = Array.from([1, 2, 3], (i) =>
    document.getElementById(`opponent-cards-${i}`)
);
export const myCardsContainer = document.getElementById('my-cards');
export const dealer = document.getElementById('dealer');
export const makeMoveBtn = document.getElementById('make-move-button');