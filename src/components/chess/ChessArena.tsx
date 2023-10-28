import { FC } from "hono/jsx"
import type { ChessGamePresenter } from "../../business-logic/view-domain.js"
import { ChessBoard } from "./ChessBoard.js"
import { ChessPieceAvailableTargets } from "./ChessPieceAvailableTargets.js"
import { ChessPieces } from "./ChessPieces.js"

export type ChessArenaProps = {
  boardId: string
  gamePresenter: ChessGamePresenter
}

export const ChessArena: FC<ChessArenaProps> = ({ boardId, gamePresenter }) => {
  const containersBasesClasses = "absolute inset-0 pointer-events-none"
  return (
    <div class="aspect-square relative" id={`chess-board-components-${boardId}`}>
      <div
        class="absolute inset-0 pointer-events-none z-0"
        id={`chess-board-container-${boardId}`}
      >
        <div
          class={`${containersBasesClasses} z-0`}
          id={`chess-board-container-${boardId}`}
        >
          <ChessBoard boardId={boardId} />
        </div>
        <div
          class={`${containersBasesClasses} z-20`}
          id={`chess-pieces-container-${boardId}`}
        >
          <ChessPieces gamePresenter={gamePresenter} boardId={boardId} />
        </div>
        <div
          class={`${containersBasesClasses} z-30`}
          id={`chess-available-targets-container-${boardId}`}
        >
          <ChessPieceAvailableTargets gamePresenter={gamePresenter} boardId={boardId} />
        </div>
      </div>
    </div>
  )
}
