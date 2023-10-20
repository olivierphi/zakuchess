import { FC } from "hono/jsx"
import {
  PIECE_TYPE_TO_PIECE_NAME_MAP,
  type PieceRole,
  type PieceType,
  type PlayerSide,
} from "business-logic/chess-domain.js"
import { CHESS_PIECE_Z_INDEXES } from "./ChessBoard.js"

export type ChessUnitSymbolDisplayProps = {
  role: PieceRole
}

export const ChessUnitSymbolDisplay: FC<ChessUnitSymbolDisplayProps> = ({
  role: [side, type],
}) => {
  const [isKnight, isPawn] = [type === "n", type === "p"]

  const symbolClasses = [
    // We have to do some ad-hoc adjustments for Knights and Pawns:
    isPawn || isKnight ? "w-7" : "w-8",
    "aspect-square",
    "bg-no-repeat",
    "bg-cover",
    "opacity-90",
    side == "w" ? "drop-shadow-piece-symbol-w" : "drop-shadow-piece-symbol-b",
    PIECE_SYMBOLS_CLASSES[side][type],
  ]
  const symbolDisplay = <div class={symbolClasses.join(" ")}></div>

  const symbolDisplayContainerClasses = [
    "absolute",
    "top-0",
    side == "w" ? "left-0" : "right-0",
    CHESS_PIECE_Z_INDEXES["symbol"],
    // Quick custom display for white knights, so they face the inside of the board:
    side == "w" && isKnight ? "-scale-x-100" : "",
  ]

  return (
    <div
      class={symbolDisplayContainerClasses.join(" ")}
      aria-label={PIECE_TYPE_TO_PIECE_NAME_MAP[type]}
    >
      {symbolDisplay}
    </div>
  )
}

const PIECE_SYMBOLS_CLASSES: Record<PlayerSide, Record<PieceType, string>> = {
  // We need Tailwind to see these classes, so that it bundles them in the final CSS file.
  w: {
    p: "bg-w-pawn",
    n: "bg-w-knight",
    b: "bg-w-bishop",
    r: "bg-w-rook",
    q: "bg-w-queen",
    k: "bg-w-king",
  },
  b: {
    p: "bg-b-pawn",
    n: "bg-b-knight",
    b: "bg-b-bishop",
    r: "bg-b-rook",
    q: "bg-b-queen",
    k: "bg-b-king",
  },
}
