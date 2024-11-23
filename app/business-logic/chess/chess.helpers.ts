import type {
    ChessFile,
    ChessRank,
    ChessSquare,
    PieceID,
    PieceOnBoard,
    PieceState,
    PieceSymbol,
    PlayerSide,
} from "./chess.domain.ts"

export const squareToFileAndRank = (square: ChessSquare): [ChessFile, ChessRank] => {
    return [square[0] as ChessFile, square[1] as ChessRank]
}

export const pieceSymbolFromPieceState = (state: PieceState): PieceSymbol => {
    return state[0].toLowerCase() as PieceSymbol
}

const _PIECE_SYMBOL_TO_PIECE_BOARD_MAPPING: Record<
    PlayerSide,
    Record<PieceSymbol, PieceOnBoard>
> = {
    w: {
        p: "P",
        n: "N",
        b: "B",
        r: "R",
        q: "Q",
        k: "K",
    },
    b: {
        p: "p",
        n: "n",
        b: "b",
        r: "r",
        q: "q",
        k: "k",
    },
}

export const pieceOnBoardFromPieceSymbol = (
    pieceSymbol: PieceSymbol,
    playerSide: PlayerSide,
): PieceOnBoard => {
    return _PIECE_SYMBOL_TO_PIECE_BOARD_MAPPING[playerSide][pieceSymbol]
}

export const pieceOnBoardFromPieceState = (state: PieceState): PieceOnBoard => {
    return state[0] as PieceOnBoard
}

export const playerSideFromPieceState = (state: PieceState): PlayerSide => {
    return playerSideFromPieceOnBoard(pieceOnBoardFromPieceState(state))
}

export const pieceIDFromPieceState = (state: PieceState): PieceID => {
    return state.slice(0, 2) as PieceID
}

export const playerSideFromPieceOnBoard = (piece: PieceOnBoard): PlayerSide => {
    return piece.toUpperCase() === piece ? "w" : "b"
}

export const getActivePlayerSideFromFen = (fen: string): PlayerSide => {
    return fen.split(" ")[1] as PlayerSide
}
