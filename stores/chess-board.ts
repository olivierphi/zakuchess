import type { FEN } from "#shared/business-logic/chess/chess-domain"
import { Chess, DEFAULT_POSITION } from "chess.js"

type ChessBoardStoreState = {
    fen: FEN
}

export const chessBoardStoreFactory = ({ boardId }: { boardId: string }) => {
    return defineStore(`chess-board-${boardId}`, {
        state: (): ChessBoardStoreState => {
            return {
                fen: DEFAULT_POSITION,
            }
        },
        getters: {
            chessBoard(state): Chess {
                return new Chess(state.fen)
            },
            pieces(state) {
                return this.chessBoard.pieces()
            },
        },
    })
}

export type ChessBoardStore = ReturnType<typeof chessBoardStoreFactory>
