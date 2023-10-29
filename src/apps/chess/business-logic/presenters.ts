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
  playerSideToHighlightAllPiecesFor?: PlayerSide
}

export abstract class BaseChessGamePresenter implements ChessGamePresenter {
  public readonly fen: FEN
  public readonly teams: Record<PlayerSide, TeamMember[]>
  public readonly pieceStateBySquare: PieceStateBySquare
  public readonly selectedSquare: ChessGameSelectedSquarePresenter | null = null
  public readonly selectedPiece: ChessGameSelectedPiecePresenter | null = null
  public readonly playerSideToHighlightAllPiecesFor: PlayerSide | null

  private cacheStorage: Record<string, unknown> = {}

  constructor({
    fen,
    teams,
    pieceStateBySquare,
    selectedSquare,
    selectedPieceSquare,
    playerSideToHighlightAllPiecesFor,
  }: BaseChessGamePresenterArgs) {
    this.fen = fen
    this.teams = teams
    this.pieceStateBySquare = pieceStateBySquare
    this.playerSideToHighlightAllPiecesFor = playerSideToHighlightAllPiecesFor ?? null

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

  get squaresWithPiecesThatCanMove(): ChessSquare[] {
    return this.cache("squaresWithPiecesThatCanMove", () => {
      return this.chessBoard
        .moves({ verbose: true })
        .map((move) => move.from as ChessSquare)
    })
  }

  get activePlayerSide(): PlayerSide {
    return this.chessBoard.turn()
  }

  get isInCheck(): boolean {
    return this.chessBoard.isCheck()
  }

  pieceStateAtSquare(square: ChessSquare): PieceState | null {
    return this.pieceStateBySquare[square] ?? null
  }

  abstract get isPlayerTurn(): boolean
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

  get teamMember(): TeamMember {
    return this.cache("teamMember", () => {
      const playerSide = this.gamePresenter.selectedPiece
        ? this.gamePresenter.selectedPiece.playerSide
        : this.gamePresenter.activePlayerSide
      const pieceState = this.pieceAt!
      const pieceID = pieceIDFromPieceState(pieceState)
      return this.gamePresenter.teamMembersByIDBySide[playerSide][pieceID]!
    })
  }

  get pieceAt(): PieceState | null {
    return this.cache("pieceAt", () => {
      return this.gamePresenter.pieceStateAtSquare(this.square)
    })
  }

  get playerSide(): PlayerSide {
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

  isPotentialCapture(square: ChessSquare): boolean {
    return Boolean(this.pieceAt && this.availableTargets.includes(square))
  }
}
