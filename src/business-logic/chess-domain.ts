export const FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"] as const
export const RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"] as const
export const SQUARES: Readonly<ChessSquare[]> = FILE_NAMES.map((file) => {
  return RANK_NAMES.map((rank) => {
    return `${file}${rank}` as ChessSquare
  })
}).flat()

export type ChessFile = (typeof FILE_NAMES)[number]
export type ChessRank = (typeof RANK_NAMES)[number]
export type ChessSquare = `${ChessFile}${ChessRank}`
