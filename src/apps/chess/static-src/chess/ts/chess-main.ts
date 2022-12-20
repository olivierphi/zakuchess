function cursorIsNotOnChessBoardInteractiveElement(boardId: string): boolean {
    // Must return `true` only if the user hasn't clicked on one of the game clickable elements.
    // @link https://htmx.org/attributes/hx-trigger/
    console.log("cursorIsNotOnChessBoardInteractiveElement; args=", arguments)

    const chessBoardContainer = document.getElementById(`chess-board-container-${boardId}`)

    if (chessBoardContainer === null) {
        return false // not much we can do, as it seems that this chess board has mysteriously disappeared 🤷
    }

    const chessBoardState = (chessBoardContainer.querySelector("[data-board-state]") as HTMLElement).dataset.boardState

    console.log("chessBoardState; ", chessBoardState)

    if (chessBoardState === "waiting_for_player_selection") {
        return false // there's no current selection, so we actually have nothing to do here
    }

    const hoveredElements = Array.from(document.querySelectorAll(":hover"))

    const gamePiecesElements = chessBoardContainer.querySelectorAll(".chess-board-pieces .piece")
    for (const pieceElement of gamePiecesElements) {
        if (hoveredElements.includes(pieceElement)) {
            return false // don't actually cancel the selection
        }
    }
    const selectedPieceTargetsElements = chessBoardContainer.querySelectorAll(".chess-board-available-targets .target")
    for (const targetElement of selectedPieceTargetsElements) {
        if (hoveredElements.includes(targetElement)) {
            return false // ditto
        }
    }
    return true
}

console.log("cursorIsNotOnChessBoardInteractiveElement has arrived")

window.cursorIsNotOnChessBoardInteractiveElement = cursorIsNotOnChessBoardInteractiveElement
