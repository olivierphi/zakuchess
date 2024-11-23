import { Chess } from "chess.js"

import type { ChessSquare, FEN, PieceOnBoard, PlayerSide } from "./chess.domain.ts"
import { pieceOnBoardFromPieceSymbol } from "./chess.helpers.ts"

export type ChessBoardState = {
    fen: FEN
    currentPlayer: PlayerSide
    isCheckmate: boolean
    pieces: Partial<Record<ChessSquare, PieceOnBoard>>
}

export function getBoardState({ fen }: { fen: FEN }): ChessBoardState {
    const chess = new Chess(fen)

    const pieces: Partial<Record<ChessSquare, PieceOnBoard>> = {}
    chess.board().forEach((row) => {
        row.forEach((piece) => {
            if (!piece) {
                return
            }
            pieces[piece.square] = pieceOnBoardFromPieceSymbol(piece.type, piece.color)
        })
    })

    return {
        fen,
        currentPlayer: chess.turn(),
        isCheckmate: chess.isCheckmate(),
        pieces,
    }
}
