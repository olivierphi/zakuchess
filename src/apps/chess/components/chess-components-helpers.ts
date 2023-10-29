import type { ChessFile, ChessRank, ChessSquare } from "../business-logic/chess-domain.js"
import { squareToFileAndRank } from "../business-logic/chess-helpers.js"

const _PIECE_FILE_TO_TAILWIND_POSITIONING_CLASS: Readonly<Record<ChessFile, string>> = {
  a: "translate-y-0/1",
  b: "translate-y-1/1",
  c: "translate-y-2/1",
  d: "translate-y-3/1",
  e: "translate-y-4/1",
  f: "translate-y-5/1",
  g: "translate-y-6/1",
  h: "translate-y-7/1",
}
const _PIECE_RANK_TO_TAILWIND_POSITIONING_CLASS: Readonly<Record<ChessRank, string>> = {
  "1": "translate-x-0/1",
  "2": "translate-x-1/1",
  "3": "translate-x-2/1",
  "4": "translate-x-3/1",
  "5": "translate-x-4/1",
  "6": "translate-x-5/1",
  "7": "translate-x-6/1",
  "8": "translate-x-7/1",
}

export const squareToPieceTailwindClasses = (square: ChessSquare): [string, string] => {
  const [file, rank] = squareToFileAndRank(square)
  return [
    _PIECE_FILE_TO_TAILWIND_POSITIONING_CLASS[file],
    _PIECE_RANK_TO_TAILWIND_POSITIONING_CLASS[rank],
  ]
}
