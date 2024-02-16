import type { Square } from "chess.js"

const BEST_MOVE_STOCKFISH_ANSWER_PATTERN = /^bestmove ([a-h][1-8])([a-h][1-8])/
const SCORE_STOCKFISH_ANSWER_PATTERN = / score cp (-?\d+)/

const wasmSupported =
    typeof WebAssembly === "object" &&
    WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00))

let botStockfishWorker: Worker | null = null

type WorkerEvent = Event & { data: string }

export async function playFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
    stockfishWorker: Worker | null = null,
): Promise<[Square, Square]> {
    if (!stockfishWorker) {
        if (!botStockfishWorker) {
            const chessBotDataHolder = getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId)
            botStockfishWorker = await getStockfishWorker(chessBotDataHolder)
        }
        stockfishWorker = botStockfishWorker
    }

    console.log("onBotInitialized ; initialize with fen: ", fen)
    stockfishWorker.postMessage("position fen " + fen)
    stockfishWorker.postMessage("go depth " + depth)

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.debug("onStockFishMessage", e.data)
            const bestMoveAnswerMatch = BEST_MOVE_STOCKFISH_ANSWER_PATTERN.exec(e.data)
            if (!bestMoveAnswerMatch) {
                return
            }
            stockfishWorker!.removeEventListener("message", onStockFishMessage)
            console.log("bestMoveAnswerMatch: ", [bestMoveAnswerMatch[1], bestMoveAnswerMatch[2]])
            resolve([bestMoveAnswerMatch[1] as Square, bestMoveAnswerMatch[2] as Square])
        }

        stockfishWorker!.addEventListener("message", onStockFishMessage)
    })
}

export async function getScoreFromFEN(
    fen: string,
    depth: number,
    botAssetsDataHolderElementId: string,
    stockfishWorker: Worker | null = null,
): Promise<number> {
    if (!stockfishWorker) {
        if (!botStockfishWorker) {
            const chessBotDataHolder = getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId)
            botStockfishWorker = await getStockfishWorker(chessBotDataHolder)
        }
        stockfishWorker = botStockfishWorker
    }

    console.log("onBotInitialized ; initialize with fen: ", fen)
    stockfishWorker.postMessage("position fen " + fen)

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.debug("onStockFishMessage", e.data)
            const scoreAnswerMatch = SCORE_STOCKFISH_ANSWER_PATTERN.exec(e.data)
            if (!scoreAnswerMatch) {
                return
            }
            botStockfishWorker!.removeEventListener("message", onStockFishMessage)
            console.log("scoreAnswerMatch: ", scoreAnswerMatch[1])
            resolve(parseInt(scoreAnswerMatch[1], 10))
        }

        botStockfishWorker!.addEventListener("message", onStockFishMessage)
        botStockfishWorker!.postMessage("go depth " + depth)
    })
}

export async function getStockfishWorker(botAssetsDataHolderElement: HTMLElement): Promise<Worker> {
    const chessBotData = JSON.parse(botAssetsDataHolderElement.dataset.stockfishUrls!)
    const stockfish = new Worker(wasmSupported ? chessBotData["wasm"] : chessBotData["js"])

    return new Promise((resolve, reject) => {
        function onStockFishMessage(e: WorkerEvent) {
            console.log(e.data)
            if (e.data !== "uciok") {
                return
            }
            console.debug("resolve getStockfishWorker()")
            stockfish!.removeEventListener("message", onStockFishMessage)
            resolve(stockfish!)
        }
        stockfish.addEventListener("message", onStockFishMessage)
        stockfish.postMessage("uci")
    })
}

function getBotAssetsDataHolderElementFromId(botAssetsDataHolderElementId: string): HTMLElement {
    const chessBotDataHolder = document.getElementById(botAssetsDataHolderElementId)
    if (!chessBotDataHolder) {
        throw `no #${botAssetsDataHolderElementId} element found to read bot assets data!`
    }
    return chessBotDataHolder
}
