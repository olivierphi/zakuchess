import type { ChessGamePresenter } from "business-logic/chess-domain.js"
import { FC } from "hono/jsx"
import { ChessPiece } from "./ChessPiece.js"

export type ChessPiecesProps = {
  gamePresenter: ChessGamePresenter
}
export const ChessPieces: FC<ChessPiecesProps> = ({ gamePresenter }) => {
  return (
    <div class="absolute inset-0 pointer-events-none z-10">
      {gamePresenter.pieces.map(({ square, role }) => {
        return (
          <ChessPiece square={square} role={role} factions={gamePresenter.factions} />
        )
      })}
    </div>
  )
}
