import { type FC } from "hono/jsx"
import { type ChessGamePresenter } from "../business-logic/view-domain.js"
import { ChessPiece } from "./ChessPiece.js"

export type ChessPiecesProps = {
  boardId: string
  gamePresenter: ChessGamePresenter
}
export const ChessPieces: FC<ChessPiecesProps> = ({ gamePresenter, boardId }) => {
  return (
    <div
      class="absolute inset-0 pointer-events-none z-10"
      id={`chess-board-pieces-${boardId}`}
    >
      {gamePresenter.pieces.map(({ square, state }) => {
        return (
          <ChessPiece
            boardId={boardId}
            gamePresenter={gamePresenter}
            square={square}
            state={state}
          />
        )
      })}
    </div>
  )
}
