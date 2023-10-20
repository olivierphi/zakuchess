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

export type FEN = string

export type PieceName = "pawn" | "knight" | "bishop" | "rook" | "queen" | "king"
export type PieceType = "p" | "n" | "b" | "r" | "q" | "k"
export type PlayerSide = "w" | "b"
export type PieceRoleIndex = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
export type PieceRole = [PlayerSide, PieceType, PieceRoleIndex]

export type GameFactions = Record<PlayerSide, Faction>

export type Faction = "humans" | "undeads" // more to come?

export type GamePiece = { square: ChessSquare; role: PieceRole }

export const PIECE_TYPE_TO_PIECE_NAME_MAP: Record<PieceType, PieceName> = {
  p: "pawn",
  n: "knight",
  b: "bishop",
  r: "rook",
  q: "queen",
  k: "king",
}
