import { Chess } from "chess.js"
import type {
  ChessSquare,
  FEN,
  GameFactions,
  GamePiece,
  PieceType,
  PlayerSide,
} from "./chess-domain.js"
import { ChessGamePresenter, ChessGamePresenterUrls } from "./view-domain.js"

export abstract class BaseChessGamePresenter implements ChessGamePresenter {
  public readonly fen: FEN

  private _cacheStorage: Record<string, unknown> = {}

  constructor({ fen }: { fen: FEN }) {
    this.fen = fen
  }

  get factions(): GameFactions {
    return {
      // TODO: de-harcode this
      w: "humans",
      b: "undeads",
    }
  }

  get pieces(): GamePiece[] {
    return this.cache("pieces", () => {
      return this.chessBoard
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
    })
  }

  abstract get urls(): ChessGamePresenterUrls

  protected get chessBoard(): Chess {
    return this.cache("chessBoard", () => {
      return new Chess(this.fen)
    })
  }

  protected cache<T>(cacheKey: string, valueInitialisation: () => T): T {
    if (cacheKey in this._cacheStorage) {
      return this._cacheStorage as T
    }
    const value = valueInitialisation()
    this._cacheStorage[cacheKey] = value
    return value
  }
}
