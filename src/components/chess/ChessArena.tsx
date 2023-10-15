import { FC } from "hono/jsx"
import { ChessBoard } from "./ChessBoard.js"

export type ChessArenaProps = {
  boardID?: string
}

export const ChessArena: FC<ChessArenaProps> = (props) => {
  const boardID = props.boardID || "main"

  return (
    <div class="aspect-square relative" id={`chess-board-components-${boardID}`}>
      <div
        class="absolute inset-0 pointer-events-none z-0"
        id={`chess-board-container-${boardID}`}
      >
        <ChessBoard />
      </div>
    </div>
  )
}
