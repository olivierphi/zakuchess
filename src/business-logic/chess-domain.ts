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

export type PlayerSide = "w" | "b"
export type PieceSymbol = "p" | "n" | "b" | "r" | "q" | "k"
export type PieceName = "pawn" | "knight" | "bishop" | "rook" | "queen" | "king"

// prettier-ignore
export type PieceOnBoard =
  // ----- "w" player side:
  | "P" | "N" | "B" | "R" | "Q" | "K"
  // ----- "b" player side:
  | "p" | "n" | "b" | "r" | "q" | "k"
export type PieceIDIndex = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8
// prettier-ignore
export type PieceID =
  // 8 pawns, "w" player side:
  | "P1" | "P2" | "P3" | "P4" | "P5" | "P6" | "P7" | "P8"
  // Same, "b" player side:
  | "p1" | "p2" | "p3" | "p4" | "p5" | "p6" | "p7" | "p8"
  //  8 pieces, "w" player side:
  | "N1" | "N2" | "B1" | "B2" | "R1" |  "B2" | "Q" |  "K"
  // Same, "b" player side:
  | "n1" | "n2" | "b1" | "b2" | "r1" |  "b2" | "q" |  "k"
export type Promotion = "q" | "r" | "b" | "n"
export type PieceState = `${PieceID}${Promotion | ""}`

export type GameFactions = Record<PlayerSide, Faction>

export type Faction = "humans" | "undeads" // more to come?

export type GamePiece = { square: ChessSquare; state: PieceState }

export type PieceStateBySquare = Partial<Record<ChessSquare, PieceState>>

export type TeamMember = {
  id: PieceID
  faction: Faction
  name?: [string, string]
}

export type TeamMembersByIDBySide = Record<
  PlayerSide,
  Partial<Record<PieceID, TeamMember>>
>

export const PIECE_SYMBOL_TO_PIECE_NAME_MAP: Record<PieceSymbol, PieceName> = {
  p: "pawn",
  n: "knight",
  b: "bishop",
  r: "rook",
  q: "queen",
  k: "king",
}
