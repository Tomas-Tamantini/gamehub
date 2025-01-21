export const playerIdKey = 'ghPlayerId';

export const logout = state => {
    localStorage.removeItem(playerIdKey);
    return {
        ...state,
        playerId: null
    }
}

export const login = (state, playerId) => {
    localStorage.setItem(playerIdKey, playerId);
    return {
        ...state,
        playerId
    }
}