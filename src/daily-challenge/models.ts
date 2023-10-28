import type {
  FEN,
  PieceStateBySquare,
  PlayerSide,
  TeamMember,
} from "../business-logic/chess-domain.js"

export type DailyChallenge = {
  lookupKey: string
  fen: FEN
  pieceStateBySquare: PieceStateBySquare
  teams: Record<PlayerSide, TeamMember[]>
  mySide: PlayerSide
  botSide: PlayerSide
}
