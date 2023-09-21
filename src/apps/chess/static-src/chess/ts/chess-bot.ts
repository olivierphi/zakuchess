import type { Square } from "chess.js"

const BEST_MOVE_STOCKFISH_ANSWER_PATTERN = /^bestmove ([a-h][1-8])([a-h][1-8])/
const SCORE_STOCKFISH_ANSWER_PATTERN = / score cp (-?\d+)/

const wasmSupported =
    typeof WebAssembly === "object" &&
    WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00))

let botInitializationDone = false
let stockfish: Worker | null = null

type WorkerEvent = Event & { data: string }

// TODO: decouple this from HTMX

export async function playFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
): Promise<[Square, Square]> {
    await initBot(botAssetsDataHolderElementId)

    console.log("onBotInitialized ; initialize with fen: ", fen)
    stockfish!.postMessage("position fen " + fen)

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.debug("onStockFishMessage", e.data)
            const bestMoveAnswerMatch = BEST_MOVE_STOCKFISH_ANSWER_PATTERN.exec(e.data)
            if (!bestMoveAnswerMatch) {
                return
            }
            stockfish!.removeEventListener("message", onStockFishMessage)
            console.log("bestMoveAnswerMatch: ", [bestMoveAnswerMatch[1], bestMoveAnswerMatch[2]])
            resolve([bestMoveAnswerMatch[1] as Square, bestMoveAnswerMatch[2] as Square])
        }

        stockfish!.addEventListener("message", onStockFishMessage)
        stockfish!.postMessage("go depth " + depth)
    })
}

export async function getScoreFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
): Promise<number> {
    await initBot(botAssetsDataHolderElementId)

    console.log("onBotInitialized ; initialize with fen: ", fen)
    stockfish!.postMessage("position fen " + fen)

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.debug("onStockFishMessage", e.data)
            const scoreAnswerMatch = SCORE_STOCKFISH_ANSWER_PATTERN.exec(e.data)
            if (!scoreAnswerMatch) {
                return
            }
            stockfish!.removeEventListener("message", onStockFishMessage)
            console.log("scoreAnswerMatch: ", scoreAnswerMatch[1])
            resolve(parseInt(scoreAnswerMatch[1], 10))
        }

        stockfish!.addEventListener("message", onStockFishMessage)
        stockfish!.postMessage("go depth " + depth)
    })
}

async function initBot(botAssetsDataHolderElementId: string): Promise<void> {
    if (botInitializationDone) {
        return Promise.resolve()
    }

    const chessBotDataHolder = document.getElementById(botAssetsDataHolderElementId)
    if (!chessBotDataHolder) {
        throw `no #${botAssetsDataHolderElementId} element found to read bot assets data!`
    }
    const chessBotData = JSON.parse(chessBotDataHolder.dataset.stockfishUrls!)
    stockfish = new Worker(wasmSupported ? chessBotData["wasm"] : chessBotData["js"])

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.log(e.data)
            if (e.data !== "uciok") {
                return
            }
            botInitializationDone = true
            console.debug("resolve initBot()")
            stockfish!.removeEventListener("message", onStockFishMessage)
            resolve()
        }
        stockfish!.addEventListener("message", onStockFishMessage)
        stockfish!.postMessage("uci")
    })
}
