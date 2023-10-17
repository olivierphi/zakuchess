import type {
  ChessGamePresenter,
  ChessSquare,
  FEN,
  GameFactions,
  GamePiece,
  PieceType,
  PlayerSide,
} from "./chess-domain.js"
import { Chess } from "chess.js"

export class BaseChessGamePresenter implements ChessGamePresenter {
  protected _fen: FEN

  protected _cache: Record<string, unknown> = {}

  constructor({ fen }: { fen: FEN }) {
    this._fen = fen
  }

  get factions(): GameFactions {
    return {
      // TODO: de-harcode this
      w: "humans",
      b: "undeads",
    }
  }

  get fen(): FEN {
    return this._fen
  }

  get pieces(): GamePiece[] {
    if (!this._cache.pieces) {
      const pieces: GamePiece[] = this.chessBoard
        .board()
        .flat()
        .filter((piece) => !!piece)
        .map((piece) => {
          piece = piece! // guaranteed by the filter above
          return {
            square: piece.square as ChessSquare,
            // TODO: make the "piece number" dynamic, from the game's state
            role: [piece.color as PlayerSide, piece.type as PieceType, 1],
          }
        })
      this._cache.pieces = pieces
    }
    return this._cache.pieces as GamePiece[]
  }

  private get chessBoard(): Chess {
    if (!this._cache.chessBoard) {
      this._cache.chessBoard = new Chess(this.fen)
    }
    return this._cache.chessBoard as Chess
  }
}
