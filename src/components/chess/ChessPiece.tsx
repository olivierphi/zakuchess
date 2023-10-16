import type { ChessSquare, PieceType, PlayerSide } from "business-logic/chess-domain.js"
import { squareToPieceTailwindClasses } from "components/chess-components-helpers.js"
import { FC } from "hono/jsx"

export const ChessPiece: FC<{
  piece: { square: ChessSquare; type: PieceType; side: PlayerSide }
}> = ({ piece: { square, type, side } }) => {
  const isGameOver = false //TODO
  const classes = [
    "absolute",
    "aspect-square",
    "w-1/8",
    ...squareToPieceTailwindClasses(square),
    isGameOver ? "cursor-default" : "cursor-pointer",
    isGameOver ? "pointer-events-none" : "pointer-events-auto",
    // Transition-related classes:
    "transition-coordinates",
    "duration-300",
    "ease-in",
    "transform-gpu",
  ]

  return <div class={classes.join(" ")}>{type}</div>
}
