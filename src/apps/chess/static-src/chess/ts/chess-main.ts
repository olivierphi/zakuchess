import { playFromFEN, getScoreFromFEN } from "./chess-bot"

// @ts-ignore
window.cursorIsNotOnChessBoardInteractiveElement = cursorIsNotOnChessBoardInteractiveElement
// @ts-ignore
window.playBotMove = playBotMove
// @ts-ignore
window.computeScore = computeScore
// @ts-ignore
window.closeSpeechBubble = closeSpeechBubble
// @ts-ignore
window.__admin__playFromFEN = playFromFEN

function cursorIsNotOnChessBoardInteractiveElement(boardId: string): boolean {
    // Must return `true` only if the user hasn't clicked on one of the game clickable elements.
    // @link https://htmx.org/attributes/hx-trigger/
    // (see our "chess_arena" Python component to see it used)

    const chessBoardContainer = document.getElementById(`chess-arena-${boardId}`)

    if (chessBoardContainer === null) {
        return false // not much we can do, as it seems that this chess board has mysteriously disappeared 🤷
    }

    const chessBoardState = (chessBoardContainer.querySelector("[data-board-state]") as HTMLElement).dataset
        .boardState as string

    console.log("chessBoardState; ", chessBoardState)

    if (chessBoardState === "waiting_for_player_selection") {
        return false // there's no current selection, so we actually have nothing to do here
    }
    if (chessBoardState === "waiting_for_bot_turn") {
        // As we're 100% server-side-rendered in this 1st version, de-selecting a piece
        // triggers a HTMX refresh of the board, which may conflict with the wait for
        // the bot's move.
        // --> let's not allow de-selecting a piece when it's the bot's turn.
        return false
    }

    if (chessBoardState.includes("game_over")) {
        return false // the UI stops being interactive when the game is over
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
        return false // don't actually cancel the selection when clicking on the "restart daily challenge" button
    }

    const speechBubble = getSpeechBubble()
    if (speechBubble && hoveredElements.includes(speechBubble)) {
        return false // don't actually cancel the selection when closing the speech bubble
    }

    const modalContainer = document.getElementById("modal-container")
    if (modalContainer && hoveredElements.includes(modalContainer)) {
        return false // don't actually cancel the selection when interacting with a modal
    }

    console.log("no interactive UI element clicked: we reset the board state")
    return true
}

type BotMoveDescription = {
    fen: string
    htmxElementId: string
    botAssetsDataHolderElementId: string
    forcedMove: [string, string] | null
    depth: number
}

function playBotMove({
    fen,
    htmxElementId,
    botAssetsDataHolderElementId,
    forcedMove,
    depth,
}: BotMoveDescription): void {
    const htmxElement = document.getElementById(htmxElementId)
    if (!htmxElement) {
        throw `no #${botAssetsDataHolderElementId} element found to play bot's move!`
    }

    const doPlayBotMove = (from: string, to: string) => {
        const targeUrlPattern = htmxElement.dataset.hxPost!
        const targeUrl = targeUrlPattern.replace("<from>", from).replace("<to>", to)
        htmxElement.dataset.hxPost = targeUrl
        window.htmx.process(htmxElement)
        window.htmx.trigger(htmxElement, "playMove", {})
    }

    if (forcedMove) {
        doPlayBotMove(forcedMove[0], forcedMove[1])
        return
    }

    playFromFEN(fen, depth, botAssetsDataHolderElementId).then((move) => {
        console.log(`bot wants to move from ${move[0]} to ${move[1]}`)
        doPlayBotMove(move[0], move[1])
    })
}

function computeScore(fen: string, botAssetsDataHolderElementId: string): Promise<number> {
    return getScoreFromFEN(fen, 2, botAssetsDataHolderElementId).then((score) => {
        console.log(`Stockfish says score is ${score}`)
        return score
    })
}

function closeSpeechBubble() {
    const speechBubble = getSpeechBubble()
    if (speechBubble && speechBubble.parentNode) {
        speechBubble.remove()
    }
}

function getSpeechBubble(): Element | null {
    return document.querySelector("[data-speech-bubble]")
}
