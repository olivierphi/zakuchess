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

    const gamePiecesElements = chessBoardContainer.querySelectorAll(`#chess-board-pieces-${boardId} [data-piece-role]`)
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

    const restartDailyChallengeButtonElement = chessBoardContainer.querySelector(
        `#chess-board-restart-daily-challenge-${boardId}`,
    )
    if (restartDailyChallengeButtonElement && hoveredElements.includes(restartDailyChallengeButtonElement)) {
        return false // don't actually cancel the selection
    }

    console.log("no interactive UI element clicked: we reset the board state")
    return true
}

function playBotMove(
    fen: string,
    htmxElementId: string,
    botAssetsDataHolderElementId: string,
    forcedMove: string | null,
): void {
    const htmxElement = document.getElementById(htmxElementId)
    if (!htmxElement) {
        throw `no #${botAssetsDataHolderElementId} element found to play bot's move!`
    }

    const doPlayBotMove = (move: string) => {
        htmxElement.dataset.hxPost = htmxElement.dataset.hxPost!.replace("BOT_MOVE", move)
        window.htmx.process(htmxElement)
        window.htmx.trigger(htmxElement, "playMove", {})
    }

    if (forcedMove) {
        doPlayBotMove(forcedMove)
        return
    }

    playFromFEN(fen, 1, botAssetsDataHolderElementId).then((move) => {
        console.log(`bot wants to move from ${move[0]} to ${move[1]}`)
        doPlayBotMove(`${move[0]}${move[1]}`)
    })
}
