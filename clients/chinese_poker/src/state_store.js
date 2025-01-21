import { playerIdKey } from "./auth_service.js";
import updateDom from "./update_dom.js";

function initialState() {
    return {
        playerId: localStorage.getItem(playerIdKey)
    }
}

class StateStore {
    constructor() {
        this.state = initialState();
    }

    action(action) {
        this.state = action(this.state);
        updateDom(this.state);
    }
}

export default new StateStore();