import { BaseChessGamePresenter } from "../business-logic/BaseChessGamePresenter.js"
import type { ChessSquare } from "../business-logic/chess-domain.js"
import type { ChessGamePresenterUrls, URLString } from "../business-logic/view-domain.js"
import type { PlayerGameState } from "./domain.js"
import type { DailyChallenge } from "./models.js"
import { routes } from "./urls.js"

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
    return routes["htmx:select-piece"]({ square, boardId })
  }
}
