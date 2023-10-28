import { FC } from "hono/jsx"
import type {
  Faction,
  GameFactions,
  PieceState,
  PieceSymbol,
  PlayerSide,
} from "business-logic/chess-domain.js"
import {
  pieceSymbolFromPieceState,
  playerSideFromPieceState,
} from "business-logic/chess-helpers.js"
import { CHESS_PIECE_Z_INDEXES } from "./ChessBoard.js"

export type ChessCharacterDisplayProps = {
  state: PieceState
  factions: GameFactions
}

export const ChessCharacterDisplay: FC<ChessCharacterDisplayProps> = ({
  state,
  factions,
}) => {
  const isActivePlayerPiece = false // TODO
  const isHighlighted = false // TODO
  const isPotentialCapture = false // TODO
  const [pieceSymbol, side] = [
    pieceSymbolFromPieceState(state),
    playerSideFromPieceState(state),
  ]

  const [isKnight, isKing] = [pieceSymbol === "n", pieceSymbol === "k"] // eslint-disable-line @typescript-eslint/no-unused-vars

  const horizontalTranslation =
    side === "w" ? (isKnight ? "left-3" : "left-0") : "right-0"
  const verticalTranslation = isKnight && side === "w" ? "top-2" : "top-1"

  const classes = [
    "relative",
    isKnight ? "w-10/12" : "w-11/12",
    "aspect-square",
    "bg-no-repeat",
    "bg-cover",
    CHESS_PIECE_Z_INDEXES["character"],
    horizontalTranslation,
    verticalTranslation,
    ...pieceCharacterClasses({ pieceSymbol, side, factions }),
    // Conditional classes:
    isHighlighted
      ? isActivePlayerPiece
        ? "drop-shadow-active-selected-piece"
        : "drop-shadow-opponent-selected-piece"
      : side === "w"
      ? "drop-shadow-piece-symbol-w"
      : "drop-shadow-piece-symbol-b",
    isPotentialCapture ? "drop-shadow-potential-capture" : "",
  ]

  return <div class={classes.join(" ")} data-piece-role={`${side}-${pieceSymbol}`}></div>
}

const _PIECE_UNITS_CLASSES: Record<Faction, Record<PieceSymbol, string>> = {
  // We need Tailwind to see these classes, so that it bundles them in the final CSS file.
  humans: {
    p: "bg-humans-pawn",
    n: "bg-humans-knight",
    b: "bg-humans-bishop",
    r: "bg-humans-rook",
    q: "bg-humans-queen",
    k: "bg-humans-king",
  },
  undeads: {
    p: "bg-undeads-pawn",
    n: "bg-undeads-knight",
    b: "bg-undeads-bishop",
    r: "bg-undeads-rook",
    q: "bg-undeads-queen",
    k: "bg-undeads-king",
  },
}

const pieceCharacterClasses = ({
  pieceSymbol,
  side,
  factions,
}: {
  pieceSymbol: PieceSymbol
  side: PlayerSide
  factions: GameFactions
}): string[] => {
  const classes = [_PIECE_UNITS_CLASSES[factions[side]][pieceSymbol]]
  if (side === "b") {
    classes.push("-scale-x-100")
  }
  return classes
}
