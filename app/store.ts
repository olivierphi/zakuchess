import { Store } from "@tanstack/react-store"

import type { FEN } from "./business-logic/chess/chess.domain"
import { getBoardState, type ChessBoardState } from "./business-logic/chess/chess-state.helpers"

type ChessGameState = {
    board: ChessBoardState,
}

type GameStore = Store<ChessGameState>
const GAME_STORES: Record<string, GameStore> = {}

export function setGameFEN(boardId: string, fen: FEN) {
    GAME_STORES[boardId].setState((state) => {
        return { ...state, board: getBoardState({ fen }) }
    })
}
