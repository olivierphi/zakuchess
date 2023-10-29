import { type FC } from "hono/jsx"
import type {
  ChessSquare,
  Faction,
  GameFactions,
  PieceState,
  PieceSymbol,
  PlayerSide,
} from "../business-logic/chess-domain.js"
import {
  pieceSymbolFromPieceState,
  playerSideFromPieceState,
} from "../business-logic/chess-helpers.js"
import type { ChessGamePresenter } from "../business-logic/view-domain.js"
import { CHESS_PIECE_Z_INDEXES } from "./ChessBoard.js"

export type ChessCharacterDisplayProps = {
  gamePresenter?: ChessGamePresenter
  factions?: GameFactions
  state: PieceState
  square?: ChessSquare
}

export const ChessCharacterDisplay: FC<ChessCharacterDisplayProps> = ({
  gamePresenter,
  factions,
  state,
  square,
}) => {
  if (!gamePresenter && !factions) {
    throw new Error(
      "Either 'gamePresenter' or 'factions' must be passed to ChessCharacterDisplay.",
    )
  }

  const [pieceSymbol, piecePlayerSide] = [
    pieceSymbolFromPieceState(state),
    playerSideFromPieceState(state),
  ]
  const isActivePlayerPiece = gamePresenter?.activePlayerSide === piecePlayerSide
  const isWSide = piecePlayerSide === "w"
  const [isKnight, isKing] = [pieceSymbol === "n", pieceSymbol === "k"] // eslint-disable-line @typescript-eslint/no-unused-vars

  let isHighlighted = false
  let isPotentialCapture = false
  if (gamePresenter) {
    if (square) {
      if (gamePresenter.selectedPiece?.square === square) {
        isHighlighted = true
      } else if (gamePresenter.playerSideToHighlightAllPiecesFor === piecePlayerSide) {
        isHighlighted = true
      }
      if (gamePresenter?.selectedPiece?.isPotentialCapture(square)) {
        isPotentialCapture = true
      }
    }
    if (!isPotentialCapture && isKing && isActivePlayerPiece && gamePresenter.isInCheck) {
      isPotentialCapture = true
    }
  }

  // Right, let's do this shall we?
  const horizontalTranslation = isWSide ? (isKnight ? "left-3" : "left-0") : "right-0"
  const verticalTranslation = isKnight && isWSide ? "top-2" : "top-1"
  const gameFactions = (gamePresenter ? gamePresenter.factions : factions) as GameFactions

  const classes = [
    "relative",
    isKnight ? "w-10/12" : "w-11/12",
    "aspect-square",
    "bg-no-repeat",
    "bg-cover",
    CHESS_PIECE_Z_INDEXES["character"],
    horizontalTranslation,
    verticalTranslation,
    ...pieceCharacterClasses({
      pieceSymbol,
      side: piecePlayerSide,
      factions: gameFactions,
    }),
    // Conditional classes:
    isHighlighted
      ? isActivePlayerPiece
        ? "drop-shadow-active-selected-piece"
        : "drop-shadow-opponent-selected-piece"
      : piecePlayerSide === "w"
      ? "drop-shadow-piece-symbol-w"
      : "drop-shadow-piece-symbol-b",
    isPotentialCapture ? "drop-shadow-potential-capture" : "",
  ]

  return <div class={classes.join(" ")} data-piece-state={state} />
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
