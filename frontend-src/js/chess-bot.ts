import type { Square } from "chess.js"

const CHESS_BOT_DATA_HOLDER_DOM_ELEMENT_ID = "chess-bot-data"

const BEST_MOVE_STOCKFISH_ANSWER_PATTERN = /^bestmove ([a-h][1-8])([a-h][1-8])/

const wasmSupported =
    typeof WebAssembly === "object" &&
    WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00))

let botInitializationDone = false
let stockfish: Worker | null = null

type WorkerEvent = Event & { data: string }

// TODO: decouple this from HTMX

export async function playFromFEN(fen: string, depth: number): Promise<[Square, Square]> {
    await initBot()

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
            console.log("bestMoveAnswerMatch: ", bestMoveAnswerMatch[2])
            resolve([bestMoveAnswerMatch[1] as Square, bestMoveAnswerMatch[2] as Square])
        }

        stockfish!.addEventListener("message", onStockFishMessage)
        stockfish!.postMessage("go depth " + depth)
    })
}

async function initBot(): Promise<void> {
    if (botInitializationDone) {
        return Promise.resolve()
    }

    const chessBotDataHolder = document.getElementById(CHESS_BOT_DATA_HOLDER_DOM_ELEMENT_ID)
    if (!chessBotDataHolder) {
        throw "no #chess-bot-data found!"
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
