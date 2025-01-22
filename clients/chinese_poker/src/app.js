import socket_service from "../../socket_service.js";
import { login, logout, playerIdKey } from "./auth_service.js";
import { authBtn, joinGameBtn, statusArea } from "./dom.js";
import state_store from "./state_store.js";

const playerId = localStorage.getItem(playerIdKey);
if (playerId) {
    state_store.action(state => login(state, playerId));
}
else {
    state_store.action(logout);
}

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


socket_service.subscribe(msg => {
    if (msg.message_type == "ERROR") {
        state_store.action(state => {
            return { ...state, statusMsg: msg.payload.error }
        })
    }
    else if (msg.message_type == "PLAYER_JOINED") {
        const statusMsg = `Players in room: ${msg.payload.player_ids.join(', ')}`;
        const roomId = msg.payload.room_id;
        state_store.action(state => {
            return { ...state, statusMsg, roomId }
        })
    }
    else if (msg.message_type == "GAME_STATE") {
        const sharedView = msg.payload.shared_view;
        if (sharedView) {
            if (sharedView.status == "START_GAME") {
                state_store.action(state => {
                    return { ...state, statusMsg: 'Game about to start!', players: sharedView.players }
                })
            }
            else if (sharedView.status == "START_MATCH") {
                state_store.action(state => {
                    return { ...state, statusMsg: 'Match about to start!' }
                })
            }
            else if (sharedView.status == "DEAL_CARDS") {
                state_store.action(state => {
                    return { ...state, statusMsg: 'Dealing cards', players: sharedView.players }
                })
            }
            else if (sharedView.status == "START_ROUND") {
                state_store.action(state => {
                    return { ...state, statusMsg: 'Starting new round', currentPlayerId: sharedView.current_player_id }
                })
            }
        }
        const private_view = msg.payload.private_view;
        if (private_view) {
            state_store.action(state => {
                return { ...state, myCards: private_view.cards }
            })
        }
        console.log(msg)
    }

})