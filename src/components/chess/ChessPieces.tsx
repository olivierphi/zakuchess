import { ChessGamePresenter } from "business-logic/ChessGamePresenter.js"
import { FC } from "hono/jsx"
import { ChessPiece } from "./ChessPiece.js"

export type ChessPiecesProps = {
  gamePresenter: ChessGamePresenter
}
export const ChessPieces: FC<ChessPiecesProps> = ({ gamePresenter }) => {
  return (
    <div class="absolute inset-0 pointer-events-none z-10">
      {gamePresenter.getPieces().map((piece) => {
        return <ChessPiece piece={piece} />
      })}
    </div>
  )
}
