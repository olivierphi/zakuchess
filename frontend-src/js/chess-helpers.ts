import { Chess, Move } from "chess.js"
import type { FEN, Square } from "./chess-domain"

const _chessInstancesCache: Record<FEN, Chess> = {}

function getChessInstance(fen: FEN): Chess {
    if (_chessInstancesCache[fen]) {
        return _chessInstancesCache[fen]
    }

    const chessInstance = new Chess(fen)
    _chessInstancesCache[fen] = chessInstance
    return chessInstance
}

export type PieceAvailableTarget = {
    square: Square
    isCapture: boolean
}
export function getPieceAvailableTargets(fen: FEN, from: Square): PieceAvailableTarget[] {
    return (getChessInstance(fen).moves({ square: from, verbose: true }) as Move[]).map((move) => {
        return {
            square: move.to as Square,
            isCapture: !!move.captured,
        }
    })
}
