import { ChessSquare, FEN, GameFactions, GamePiece } from "./chess-domain.js"

export type URLString = string

export interface ChessGamePresenter {
  readonly fen: FEN
  readonly pieces: GamePiece[]
  readonly factions: GameFactions
  readonly urls: ChessGamePresenterUrls
}

export interface ChessGamePresenterUrls {
  htmxGameNoSelection: (args: { boardId: string }) => URLString
  htmxGameSelectPiece: (args: { square: ChessSquare; boardId: string }) => URLString
  htmxGameMovePiece: (args: { square: ChessSquare; boardId: string }) => URLString
  htmxGamePlayBotMove: (args: { square: ChessSquare; boardId: string }) => URLString
}
