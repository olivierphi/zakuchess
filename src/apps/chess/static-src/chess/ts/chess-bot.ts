import type { Square } from "chess.js"

/**
 * @link https://github.com/official-stockfish/Stockfish/wiki/UCI-&-Commands
 */

const BEST_MOVE_UCI_ANSWER_PATTERN = /^bestmove ([a-h][1-8])([a-h][1-8])/
const SCORE_UCI_ANSWER_PATTERN = / score (cp|mate) (-?\d+)/

const wasmSupported =
    typeof WebAssembly === "object" &&
    WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00))
let botChessEngineWorker: Worker | null = null

type WorkerEvent = Event & { data: string }

export async function playFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
    engineWorker: Worker | null = null,
): Promise<[Square, Square]> {
    if (!engineWorker) {
        if (!botChessEngineWorker) {
            const chessBotDataHolder = getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId)
            botChessEngineWorker = await getChessEngineWorker(chessBotDataHolder)
        }
        engineWorker = botChessEngineWorker
    }

    // Fo each move we reset the engine with `ucinewgame` and `isready` commands,
    // hoping to avoid any state from previous moves to affect the next move's result:
    // since we have a "pre-calculated in the Django Admin" solution machinery,
    // we choose to prioritise determinism over performance.
    // (we're talking about a few milliseconds here, not a few seconds)
    engineWorker.postMessage("ucinewgame")
    engineWorker.postMessage("isready")
    let startTime = 0

    return new Promise((resolve, reject) => {
        function onChessEngineMessage(e: WorkerEvent) {
            console.debug("onChessEngineMessage", e.data)
            if (e.data.startsWith("readyok")) {
                engineWorker!.postMessage(`position fen ${fen}`)
                engineWorker!.postMessage(`go depth ${depth}`)
                startTime = Date.now()
                return
            }

            const bestMoveAnswerMatch = BEST_MOVE_UCI_ANSWER_PATTERN.exec(e.data)
            if (!bestMoveAnswerMatch) {
                return
            }

            engineWorker!.removeEventListener("message", onChessEngineMessage)
            console.log(
                `FEN ${fen}:`,
                "bestMoveAnswerMatch: ",
                [bestMoveAnswerMatch[1], bestMoveAnswerMatch[2]],
                `(in ${Math.round(Date.now() - startTime)}ms, depth ${depth})`,
            )
            resolve([bestMoveAnswerMatch[1] as Square, bestMoveAnswerMatch[2] as Square])
        }

        engineWorker!.addEventListener("message", onChessEngineMessage)
    })
}

// TODO: merge this function with the previous `playFromFEN` one
export async function getScoreFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
    engineWorker: Worker | null = null,
): Promise<["cp" | "mate", number]> {
    if (!engineWorker) {
        if (!botChessEngineWorker) {
            const chessBotDataHolder = getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId)
            botChessEngineWorker = await getChessEngineWorker(chessBotDataHolder)
        }
        engineWorker = botChessEngineWorker
    }

    engineWorker.postMessage("ucinewgame")
    engineWorker.postMessage("isready")
    let startTime = 0

    return new Promise((resolve, reject) => {
        function onChessEngineMessage(e: WorkerEvent) {
            console.debug("onChessEngineMessage", e.data)
            if (e.data.startsWith("readyok")) {
                engineWorker!.postMessage(`position fen ${fen}`)
                engineWorker!.postMessage(`go depth ${depth}`)
                startTime = Date.now()
                return
            }

            const scoreAnswerMatch = SCORE_UCI_ANSWER_PATTERN.exec(e.data)
            if (!scoreAnswerMatch) {
                return
            }
            botChessEngineWorker!.removeEventListener("message", onChessEngineMessage)
            console.log(
                `FEN ${fen}:`,
                "scoreAnswerMatch: ",
                scoreAnswerMatch[1],
                scoreAnswerMatch[2],
                `(in ${Math.round(Date.now() - startTime!)}ms)`,
            )
            resolve([scoreAnswerMatch[1] as "cp" | "mate", parseInt(scoreAnswerMatch[2], 10)])
        }

        engineWorker!.addEventListener("message", onChessEngineMessage)
    })
}

export async function getChessEngineWorker(botAssetsDataHolderElement: HTMLElement): Promise<Worker> {
    const chessBotData = JSON.parse(botAssetsDataHolderElement.dataset.chessEngineUrls!)
    const engineWorkerScript = chessBotData["wasm"] && wasmSupported ? chessBotData["wasm"] : chessBotData["js"]
    const engineWorker = new Worker(engineWorkerScript)

    return new Promise((resolve, reject) => {
        function onChessEngineMessage(e: WorkerEvent) {
            console.log(e.data)
            if (!e.data.startsWith("uciok")) {
                return
            }
            engineWorker!.removeEventListener("message", onChessEngineMessage)
            resolve(engineWorker!)
        }
        engineWorker.addEventListener("message", onChessEngineMessage)
        engineWorker.postMessage("uci")
    })
}

export function resetChessEngineWorker(): void {
    if (!botChessEngineWorker) {
        return
    }
    console.log("terminating bot's chess engine Worker")
    botChessEngineWorker.terminate()
    botChessEngineWorker = null
}

function getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId: string): HTMLElement {
    // See the `chess_bot_data` Python function for how it's generated
    const chessBotDataHolder = document.getElementById(botAssetsDataHolderElementId)
    if (!chessBotDataHolder) {
        throw `no #${botAssetsDataHolderElementId} element found to read bot assets data!`
    }
    return chessBotDataHolder
}
