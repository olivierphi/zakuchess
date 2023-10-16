import type { ChessSquare, FEN, PieceType, PlayerSide } from "./chess-domain.js"
import { Chess } from "chess.js"

export type GamePiece = { square: ChessSquare; type: PieceType; side: PlayerSide }

export class ChessGamePresenter {
  private fen: FEN

  private cache: Record<string, unknown> = {}

  constructor({ fen }: { fen: FEN }) {
    this.fen = fen
  }

  getFEN() {
    return this.fen
  }

  getPieces(): GamePiece[] {
    if (!this.cache.pieces) {
      const pieces: GamePiece[] = this.getChessBoard()
        .board()
        .flat()
        .filter((piece) => !!piece)
        .map((piece) => {
          return {
            square: piece?.square as ChessSquare,
            type: piece?.type as PieceType,
            side: piece?.color as PlayerSide,
          }
        })
      this.cache.pieces = pieces
    }
    return this.cache.pieces as GamePiece[]
  }

  private getChessBoard(): Chess {
    if (!this.cache.chessBoard) {
      this.cache.chessBoard = new Chess(this.fen)
    }
    return this.cache.chessBoard as Chess
  }
}
