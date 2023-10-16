import { FC } from "hono/jsx"
import { ChessBoard } from "./ChessBoard.js"
import { ChessGamePresenter } from "business-logic/ChessGamePresenter.js"
import { ChessPieces } from "./ChessPieces.js"

export type ChessArenaProps = {
  boardID?: string
  gamePresenter: ChessGamePresenter
}

export const ChessArena: FC<ChessArenaProps> = (props) => {
  const boardID = props.boardID || "main"
  const gamePresenter = props.gamePresenter

  return (
    <div class="aspect-square relative" id={`chess-board-components-${boardID}`}>
      <div
        class="absolute inset-0 pointer-events-none z-0"
        id={`chess-board-container-${boardID}`}
      >
        <ChessBoard />
        <ChessPieces gamePresenter={gamePresenter} />
      </div>
    </div>
  )
}
