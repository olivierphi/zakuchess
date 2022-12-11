import { Chess, Move, PieceSymbol } from "chess.js"
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

const UNICODE_PIECE_SYMBOLS: Record<PieceSymbol, string> = {
    // copy-pasted from chess.py
    r: "♜",
    n: "♞",
    b: "♝",
    q: "♛",
    k: "♚",
    p: "♟",
}

const PIECE_CHESS_NAMES: Record<PieceSymbol, string> = {
    // TODO: translate that?
    r: "Rook",
    n: "Knight",
    b: "Bishop",
    q: "Queen",
    k: "King",
    p: "Pawn",
}

export function getChessPieceSymbol(piece: PieceSymbol): string {
    return UNICODE_PIECE_SYMBOLS[piece]
}
export function getChessPieceName(piece: PieceSymbol): string {
    return PIECE_CHESS_NAMES[piece]
}
