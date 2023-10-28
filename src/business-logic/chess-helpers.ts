import type {
  ChessFile,
  ChessRank,
  ChessSquare,
  PieceID,
  PieceOnBoard,
  PieceState,
  PieceSymbol,
  PlayerSide,
} from "./chess-domain.js"

export const squareToFileAndRank = (square: ChessSquare): [ChessFile, ChessRank] => {
  return [square[0] as ChessFile, square[1] as ChessRank]
}

export const pieceSymbolFromPieceState = (state: PieceState): PieceSymbol => {
  return state[0].toLowerCase() as PieceSymbol
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
