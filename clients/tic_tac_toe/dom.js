export const nameInput = document.getElementById("name");
export const startGameBtn = document.getElementById("start-game");
export const statusArea = document.getElementById("status");
export const gridCells = document.querySelectorAll('.grid-cell');

export function resetGridCells() {
    gridCells.forEach((cell) => {
        cell.textContent = '';
    });
}