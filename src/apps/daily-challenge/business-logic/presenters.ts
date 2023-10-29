import type { ChessSquare } from "apps/chess/business-logic/chess-domain.js"
import { BaseChessGamePresenter } from "apps/chess/business-logic/presenters.js"
import type {
  ChessGamePresenterUrls,
  URLString,
} from "apps/chess/business-logic/view-domain.js"
import { routes } from "../urls.js"
import type { PlayerGameState } from "./domain.js"
import type { DailyChallenge } from "./models.js"

type DailyChallengeGamePresenterArgs = {
  challenge: DailyChallenge
  gameState: PlayerGameState
  selectedSquare?: ChessSquare
  selectedPieceSquare?: ChessSquare
  isPreview: boolean
}

export class DailyChallengeGamePresenter extends BaseChessGamePresenter {
  public readonly gameState: PlayerGameState

  private readonly challenge: DailyChallenge
  private readonly isPreview: boolean
  private readonly urlsPresenter: DailyChallengeGameUrlsPresenter

  constructor({
    challenge,
    gameState,
    selectedSquare,
    selectedPieceSquare,
    isPreview,
  }: DailyChallengeGamePresenterArgs) {
    super({
      fen: challenge.fen,
      teams: challenge.teams,
      pieceStateBySquare: gameState.pieceStateBySquare,
      selectedSquare,
      selectedPieceSquare,
    })
    this.challenge = challenge
    this.gameState = gameState
    this.isPreview = isPreview
    this.urlsPresenter = new DailyChallengeGameUrlsPresenter()
  }

  get isPlayerTurn(): boolean {
    return this.activePlayerSide === this.challenge.mySide
  }

  get isGameOver(): boolean {
    return false // TODO
  }

  get urls(): ChessGamePresenterUrls {
    return this.urlsPresenter
  }
}

export class DailyChallengeGameUrlsPresenter implements ChessGamePresenterUrls {
  htmxGameMovePiece({
    square,
    boardId,
  }: {
    square: ChessSquare
    boardId: string
  }): URLString {
    return `htmx/pieces/move?${new URLSearchParams({ square, boardId })}`
  }

  htmxGameNoSelection({ boardId }: { boardId: string }): URLString {
    return `htmx/no-selection?${new URLSearchParams({ boardId })}`
  }

  htmxGamePlayBotMove({
    square,
    boardId,
  }: {
    square: ChessSquare
    boardId: string
  }): URLString {
    return `htmx/bot/move?${new URLSearchParams({ square, boardId })}`
  }

  htmxGameSelectPiece({
    square,
    boardId,
  }: {
    square: ChessSquare
    boardId: string
  }): URLString {
    return routes.HTMX_SELECT_PIECE({ square, boardId })
  }
}
