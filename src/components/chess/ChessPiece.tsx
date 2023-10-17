import { FC } from "hono/jsx"
import type {
  ChessSquare,
  GameFactions,
  PieceRole,
} from "../../business-logic/chess-domain.js"
import { squareToPieceTailwindClasses } from "../chess-components-helpers.js"
import { ChessCharacterDisplay } from "./ChessCharacterDisplay.js"
import { ChessGroundMarker } from "./ChessGroundMarker.js"
import { ChessUnitSymbolDisplay } from "./ChessUnitSymbolDisplay.js"

export type ChessPieceProps = {
  square: ChessSquare
  role: PieceRole
  factions: GameFactions
}

export const ChessPiece: FC<ChessPieceProps> = ({ square, role, factions }) => {
  const [side, type] = role
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

  return (
    <div class={classes.join(" ")}>
      <ChessGroundMarker side={side} />
      <ChessCharacterDisplay side={side} pieceType={type} factions={factions} />
      <ChessUnitSymbolDisplay role={role} />
    </div>
  )
}
