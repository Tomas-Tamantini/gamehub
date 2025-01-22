export const authBtn = document.getElementById('auth-button');
export const playerIdSpan = document.getElementById('player-id');
export const joinGameBtn = document.getElementById('join-button');
export const statusArea = document.getElementById('status');
export const playerNames = Array.from({ length: 4 }, (_, i) =>
    document.getElementById(`player-name-${i}`)
);
