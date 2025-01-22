import updateDom from "./update_dom.js";



class StateStore {
    constructor() {
        this.state = {};
    }

    action(action) {
        this.state = action(this.state);
        updateDom(this.state);
    }
}

export default new StateStore();