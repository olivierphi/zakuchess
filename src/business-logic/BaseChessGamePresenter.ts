import { Chess } from "chess.js"
import type {
  ChessSquare,
  FEN,
  GameFactions,
  GamePiece,
  PieceState,
  PieceStateBySquare,
  PlayerSide,
  TeamMember,
  TeamMembersByIDBySide,
} from "./chess-domain.js"
import { pieceIDFromPieceState, playerSideFromPieceState } from "./chess-helpers.js"
import {
  ChessGamePresenter,
  ChessGamePresenterUrls,
  ChessGameSelectedPiecePresenter,
  ChessGameSelectedSquarePresenter,
} from "./view-domain.js"

export type BaseChessGamePresenterArgs = {
  fen: FEN
  teams: Record<PlayerSide, TeamMember[]>
  pieceStateBySquare: PieceStateBySquare
  selectedSquare?: ChessSquare
  selectedPieceSquare?: ChessSquare
}

export abstract class BaseChessGamePresenter implements ChessGamePresenter {
  public readonly fen: FEN
  public readonly teams: Record<PlayerSide, TeamMember[]>
  public readonly pieceStateBySquare: PieceStateBySquare
  public readonly selectedSquare: ChessGameSelectedSquarePresenter | null = null
  public readonly selectedPiece: ChessGameSelectedPiecePresenter | null = null

  private cacheStorage: Record<string, unknown> = {}

  constructor({
    fen,
    teams,
    pieceStateBySquare,
    selectedSquare,
    selectedPieceSquare,
  }: BaseChessGamePresenterArgs) {
    this.fen = fen
    this.teams = teams
    this.pieceStateBySquare = pieceStateBySquare

    if (selectedSquare) {
      this.selectedSquare = new BaseSelectedSquarePresenter({
        gamePresenter: this,
        square: selectedSquare,
        chessBoard: this.chessBoard,
      })
    }
    if (selectedPieceSquare) {
      this.selectedPiece = new BaseSelectedPiecePresenter({
        gamePresenter: this,
        square: selectedPieceSquare,
        chessBoard: this.chessBoard,
      })
    }
  }
  get teamMembersByIDBySide(): TeamMembersByIDBySide {
    return this.cache("teamMembersByIDBySide", () => {
      const teamMembersByIDBySide: TeamMembersByIDBySide = {
        w: {},
        b: {},
      }
      this.pieces.forEach((piece) => {
        const playerSide = playerSideFromPieceState(piece.state)
        const pieceID = pieceIDFromPieceState(piece.state)
        const teamMember: TeamMember = {
          id: pieceID,
          name: this.teams[playerSide].find((teamMember) => teamMember.id === pieceID)
            ?.name,
          faction: this.factions[playerSide],
        }
        teamMembersByIDBySide[playerSide][pieceID] = teamMember
      })
      return teamMembersByIDBySide
    })
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
          const square = piece.square as ChessSquare
          return {
            square,
            state: this.pieceStateBySquare[square]!,
          }
        })
    })
  }

  get activePlayerSide(): PlayerSide {
    return this.chessBoard.turn()
  }

  pieceStateAtSquare(square: ChessSquare): PieceState | null {
    return this.pieceStateBySquare[square] ?? null
  }

  abstract get isGameOver(): boolean
  abstract get urls(): ChessGamePresenterUrls

  protected get chessBoard(): Chess {
    return this.cache("chessBoard", () => {
      return new Chess(this.fen)
    })
  }

  protected cache<T>(cacheKey: string, valueInitialisation: () => T): T {
    if (cacheKey in this.cacheStorage) {
      return this.cacheStorage[cacheKey] as T
    }
    const value = valueInitialisation()
    this.cacheStorage[cacheKey] = value
    return value
  }
}

export type SelectedSquarePresenterArgs = {
  gamePresenter: ChessGamePresenter
  square: ChessSquare
  chessBoard: Chess
}

export class BaseSelectedSquarePresenter implements ChessGameSelectedSquarePresenter {
  public readonly square: ChessSquare

  protected gamePresenter: ChessGamePresenter
  protected chessBoard: Chess
  private cacheStorage: Record<string, unknown> = {}

  constructor({ gamePresenter, square, chessBoard }: SelectedSquarePresenterArgs) {
    this.gamePresenter = gamePresenter
    this.square = square
    this.chessBoard = chessBoard
  }

  public get teamMember(): TeamMember {
    return this.cache("teamMember", () => {
      const playerSide = this.gamePresenter.selectedPiece
        ? this.gamePresenter.selectedPiece.playerSide
        : this.gamePresenter.activePlayerSide
      const pieceID = pieceIDFromPieceState(
        this.gamePresenter.pieceStateAtSquare(this.square)!,
      )
      return this.gamePresenter.teamMembersByIDBySide[playerSide][pieceID]!
    })
  }

  public get playerSide(): PlayerSide {
    return this.cache("playerSide", () => {
      return playerSideFromPieceState(this.gamePresenter.pieceStateAtSquare(this.square)!)
    })
  }
  protected cache<T>(cacheKey: string, valueInitialisation: () => T): T {
    if (cacheKey in this.cacheStorage) {
      return this.cacheStorage[cacheKey] as T
    }
    const value = valueInitialisation()
    this.cacheStorage[cacheKey] = value
    return value
  }
}

export class BaseSelectedPiecePresenter
  extends BaseSelectedSquarePresenter
  implements ChessGameSelectedPiecePresenter
{
  constructor({ gamePresenter, square, chessBoard }: SelectedSquarePresenterArgs) {
    super({ gamePresenter, square, chessBoard })
  }

  get availableTargets(): ChessSquare[] {
    return this.cache("availableTargets", () => {
      return this.chessBoard
        .moves({ square: this.square, verbose: true })
        .map((move) => move.to as ChessSquare)
    })
  }
}
