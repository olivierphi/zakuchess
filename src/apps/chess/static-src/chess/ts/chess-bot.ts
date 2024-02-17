import type { Square } from "chess.js"

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

    console.log("onBotInitialized ; initialize with fen: ", fen)
    engineWorker.postMessage("position fen " + fen)
    engineWorker.postMessage("go depth " + depth)
    const startTime = Date.now()

    return new Promise((resolve, reject) => {
        function onChessEngineMessage(e: WorkerEvent) {
            console.debug("onChessEngineMessage", e.data)
            const bestMoveAnswerMatch = BEST_MOVE_UCI_ANSWER_PATTERN.exec(e.data)
            if (!bestMoveAnswerMatch) {
                return
            }
            engineWorker!.removeEventListener("message", onChessEngineMessage)
            console.log(
                "bestMoveAnswerMatch: ",
                [bestMoveAnswerMatch[1], bestMoveAnswerMatch[2]],
                `(in ${Math.round(Date.now() - startTime)}ms)`,
            )
            resolve([bestMoveAnswerMatch[1] as Square, bestMoveAnswerMatch[2] as Square])
        }

        engineWorker!.addEventListener("message", onChessEngineMessage)
    })
}

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

    console.log("onBotInitialized ; initialize with fen: ", fen)
    engineWorker.postMessage("position fen " + fen)
    const startTime = Date.now()

    return new Promise((resolve, reject) => {
        function onChessEngineMessage(e: WorkerEvent) {
            console.debug("onChessEngineMessage", e.data)
            const scoreAnswerMatch = SCORE_UCI_ANSWER_PATTERN.exec(e.data)
            if (!scoreAnswerMatch) {
                return
            }
            botChessEngineWorker!.removeEventListener("message", onChessEngineMessage)
            console.log(
                "scoreAnswerMatch: ",
                scoreAnswerMatch[1],
                scoreAnswerMatch[2],
                `(in ${Math.round(Date.now() - startTime)}ms)`,
            )
            resolve([scoreAnswerMatch[1] as "cp" | "mate", parseInt(scoreAnswerMatch[2], 10)])
        }

        engineWorker!.addEventListener("message", onChessEngineMessage)
        engineWorker!.postMessage("go depth " + depth)
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

function getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId: string): HTMLElement {
    // See the `chess_bot_data` Python function for how it's generated
    const chessBotDataHolder = document.getElementById(botAssetsDataHolderElementId)
    if (!chessBotDataHolder) {
        throw `no #${botAssetsDataHolderElementId} element found to read bot assets data!`
    }
    return chessBotDataHolder
}
