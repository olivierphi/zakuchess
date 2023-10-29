import type {
  ChessSquare,
  FEN,
  GameFactions,
  GamePiece,
  PieceState,
  PlayerSide,
  TeamMember,
  TeamMembersByIDBySide,
} from "./chess-domain.js"

export type URLString = string

export interface ChessGamePresenter {
  // Starting data:
  readonly fen: FEN
  readonly teams: Record<PlayerSide, TeamMember[]>
  readonly factions: GameFactions
  readonly urls: ChessGamePresenterUrls
  readonly selectedSquare: ChessGameSelectedSquarePresenter | null
  readonly selectedPiece: ChessGameSelectedPiecePresenter | null
  readonly playerSideToHighlightAllPiecesFor: PlayerSide | null
  // ...from which we can derive the following:
  readonly pieces: GamePiece[]
  readonly squaresWithPiecesThatCanMove: ChessSquare[]
  readonly activePlayerSide: PlayerSide
  readonly isPlayerTurn: boolean
  readonly teamMembersByIDBySide: TeamMembersByIDBySide
  readonly isInCheck: boolean
  readonly isGameOver: boolean

  pieceStateAtSquare(square: ChessSquare): PieceState | null
}

export interface ChessGamePresenterUrls {
  htmxGameNoSelection: (args: { boardId: string }) => URLString
  htmxGameSelectPiece: (args: { square: ChessSquare; boardId: string }) => URLString
  htmxGameMovePiece: (args: { square: ChessSquare; boardId: string }) => URLString
  htmxGamePlayBotMove: (args: { square: ChessSquare; boardId: string }) => URLString
}

export interface ChessGameSelectedSquarePresenter {
  readonly square: ChessSquare
  readonly teamMember: TeamMember
  readonly playerSide: PlayerSide
  readonly pieceAt: PieceState | null
}

export interface ChessGameSelectedPiecePresenter
  extends ChessGameSelectedSquarePresenter {
  readonly availableTargets: ChessSquare[]

  isPotentialCapture(square: ChessSquare): boolean
}
