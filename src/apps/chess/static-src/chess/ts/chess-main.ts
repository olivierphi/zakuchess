import { playFromFEN } from "./chess-bot"

// @ts-ignore
window.cursorIsNotOnChessBoardInteractiveElement = cursorIsNotOnChessBoardInteractiveElement
// @ts-ignore
window.playBotMove = playBotMove

function cursorIsNotOnChessBoardInteractiveElement(boardId: string): boolean {
    // Must return `true` only if the user hasn't clicked on one of the game clickable elements.
    // @link https://htmx.org/attributes/hx-trigger/
    // (see our "chess_arena" Python component to see it used)

    const chessBoardContainer = document.getElementById(`chess-arena-${boardId}`)

    if (chessBoardContainer === null) {
        return false // not much we can do, as it seems that this chess board has mysteriously disappeared 🤷
    }

    const chessBoardState = (chessBoardContainer.querySelector("[data-board-state]") as HTMLElement).dataset.boardState

    console.log("chessBoardState; ", chessBoardState)

    if (chessBoardState === "waiting_for_player_selection") {
        return false // there's no current selection, so we actually have nothing to do here
    }

    const hoveredElements = Array.from(document.querySelectorAll(":hover"))

    const gamePiecesElements = chessBoardContainer.querySelectorAll(`#chess-board-pieces-${boardId} [data-piece]`)
    for (const pieceElement of gamePiecesElements) {
        if (hoveredElements.includes(pieceElement)) {
            return false // don't actually cancel the selection
        }
    }
    const selectedPieceTargetsElements = chessBoardContainer.querySelectorAll(
        `#chess-board-available-targets-${boardId} [data-square]`,
    )
    for (const targetElement of selectedPieceTargetsElements) {
        if (hoveredElements.includes(targetElement)) {
            return false // ditto
        }
    }
    return true
}

function playBotMove(fen: string, htmxElementId: string, botAssetsDataHolderElementId: string): void {
    playFromFEN(fen, 1, botAssetsDataHolderElementId).then((move) => {
        console.log(`bot wants to move from ${move[0]} to ${move[1]}`)
        const htmxElement = document.getElementById(htmxElementId)
        if (!htmxElement) {
            throw `no #${botAssetsDataHolderElementId} element found to play bot's move!`
        }
        htmxElement.dataset.hxPost = htmxElement.dataset.hxPost!.replace("BOT_MOVE", `${move[0]}${move[1]}`)
        window.htmx.process(htmxElement)
        window.htmx.trigger(htmxElement, "playMove", {})
    })
}
