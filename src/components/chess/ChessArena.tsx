import { FC } from "hono/jsx"
import { ChessGamePresenter } from "../../business-logic/view-domain.js"
import { ChessBoard } from "./ChessBoard.js"
import { ChessPieces } from "./ChessPieces.js"

export type ChessArenaProps = {
  boardId: string
  gamePresenter: ChessGamePresenter
}

export const ChessArena: FC<ChessArenaProps> = ({ boardId, gamePresenter }) => {
  return (
    <div class="aspect-square relative" id={`chess-board-components-${boardId}`}>
      <div
        class="absolute inset-0 pointer-events-none z-0"
        id={`chess-board-container-${boardId}`}
      >
        <ChessBoard boardId={boardId} />
        <ChessPieces gamePresenter={gamePresenter} boardId={boardId} />
      </div>
    </div>
  )
}
