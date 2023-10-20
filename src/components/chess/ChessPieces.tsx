import { FC } from "hono/jsx"
import { ChessGamePresenter } from "../../business-logic/view-domain.js"
import { ChessPiece } from "./ChessPiece.js"

export type ChessPiecesProps = {
  boardId: string
  gamePresenter: ChessGamePresenter
}
export const ChessPieces: FC<ChessPiecesProps> = ({ gamePresenter, boardId }) => {
  return (
    <div class="absolute inset-0 pointer-events-none z-10">
      {gamePresenter.pieces.map(({ square, role }) => {
        return (
          <ChessPiece
            boardId={boardId}
            gamePresenter={gamePresenter}
            square={square}
            role={role}
          />
        )
      })}
    </div>
  )
}
