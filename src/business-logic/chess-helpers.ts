import type { ChessFile, ChessRank, ChessSquare } from "./chess-domain.js"

export const squareToFileAndRank = (square: ChessSquare): [ChessFile, ChessRank] => {
  return [square[0] as ChessFile, square[1] as ChessRank]
}
