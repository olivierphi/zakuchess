import { BaseChessGamePresenter } from "../business-logic/BaseChessGamePresenter.js"
import type { ChessSquare, FEN } from "../business-logic/chess-domain.js"
import type { ChessGamePresenterUrls, URLString } from "../business-logic/view-domain.js"

type DailyChallengeGamePresenterArgs = {
  fen: FEN
}

export class DailyChallengeGamePresenter extends BaseChessGamePresenter {
  private readonly _urls: DailyChallengeGameUrlsPresenter

  constructor({ fen }: DailyChallengeGamePresenterArgs) {
    super({ fen })
    this._urls = new DailyChallengeGameUrlsPresenter()
  }

  get urls(): ChessGamePresenterUrls {
    return this._urls
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
    return `htmx/pieces/select?${new URLSearchParams({ square, boardId })}`
  }
}
