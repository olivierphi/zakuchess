import { FC } from "hono/jsx"
import type { PlayerSide } from "business-logic/chess-domain.js"
import { CHESS_PIECE_Z_INDEXES } from "./ChessBoard.js"

export type ChessGroundMarkerProps = {
  side: PlayerSide
  pieceCanMove?: boolean
}

export const ChessGroundMarker: FC<ChessGroundMarkerProps> = ({ side, pieceCanMove }) => {
  const classes = [
    "absolute",
    "w-11/12",
    "h-2/5",
    "left-1/24",
    "bottom-0.5",
    "rounded-1/2",
    CHESS_PIECE_Z_INDEXES["ground_marker"],
    "border-solid",
    PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[
      `${side}-${pieceCanMove ? "canMove" : "cannotMove"}`
    ],
  ]

  return <div class={classes.join(" ")}></div>
}

type CanMoveExp = "canMove" | "cannotMove"
type ClassesKey = `${PlayerSide}-${CanMoveExp}`

const PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: Record<ClassesKey, string> = {
  // the boolean says if the piece can move
  "w-cannotMove": "bg-emerald-800/40 border-2 border-emerald-800",
  "b-cannotMove": "bg-indigo-800/40 border-2 border-indigo-800",
  "w-canMove": "bg-emerald-600/40 border-2 border-emerald-800",
  "b-canMove": "bg-indigo-600/40 border-2 border-indigo-800",
}
