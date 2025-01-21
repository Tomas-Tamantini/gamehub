import { authBtn } from "./dom.js";
import userService from "./user_service.js";

authBtn.addEventListener('click', () => {
    if (userService.isLoggedIn()) {
        userService.logout();
    }
    else {
        const playerId = prompt('Enter your player id');
        userService.login(playerId);
    }
});