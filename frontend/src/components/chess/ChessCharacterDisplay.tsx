import React from "react";
import type {
  PieceRole,
  Square,
  Faction,
  PieceName,
  BoardOrientation,
} from "@shared/chess/chess-logic.ts";
import {
  playerSideFromPieceRole,
  typeFromPieceRole,
  pieceNameFromPieceRole,
  pieceShouldFaceLeft,
} from "@shared/chess/utils.ts";
import { useChessArenaStore } from "./ChessArenaProvider.tsx";
import { CHESS_PIECE_Z_INDEXES } from "@shared/chess/chess-html-display.ts";

const PIECE_UNITS_CLASSES: Record<Faction, Record<PieceName, string>> = {
  // We need Tailwind to see these classes, so that it bundles them in the final CSS file.
  humans: {
    pawn: "bg-humans-pawn",
    knight: "bg-humans-knight",
    bishop: "bg-humans-bishop",
    rook: "bg-humans-rook",
    queen: "bg-humans-queen",
    king: "bg-humans-king",
  },
  undead: {
    pawn: "bg-undead-pawn",
    knight: "bg-undead-knight",
    bishop: "bg-undead-bishop",
    rook: "bg-undead-rook",
    queen: "bg-undead-queen",
    king: "bg-undead-king",
  },
};

interface ChessCharacterDisplayProps {
  pieceRole: PieceRole;
  boardOrientation: BoardOrientation;
  square?: Square;
  additionalClasses?: string[];
}

export const ChessCharacterDisplay: React.FC<ChessCharacterDisplayProps> = ({
  pieceRole,
  boardOrientation,
  square,
  additionalClasses = [],
}) => {
  const piecePlayerSide = playerSideFromPieceRole(pieceRole);
  const pieceType = typeFromPieceRole(pieceRole);
  const pieceName = pieceNameFromPieceRole(pieceRole);
  const isKnight = pieceType === "n";

  // Determine faction based on player side
  const faction: Faction = piecePlayerSide === "w" ? "humans" : "undead";

  // Get the Tailwind class for this piece
  const pieceBackgroundClass = PIECE_UNITS_CLASSES[faction][pieceName];

  // Get game state for highlighting logic
  const { selectedSquare, availableMoves, currentPlayer } = useChessArenaStore(
    (state) => ({
      selectedSquare: state.selectedSquare,
      availableMoves: state.availableMoves,
      currentPlayer: state.currentPlayer,
    }),
  );

  // Determine highlighting states based on Python reference logic
  // Only apply highlighting logic if we have a square position
  const isSelectedPiece = Boolean(square && selectedSquare === square);
  const isPlayable = piecePlayerSide === currentPlayer;
  // For now, only highlight the selected piece (can extend later for side highlighting)
  const isHighlighted = isSelectedPiece;

  // Check if this piece can be captured by the selected piece
  const isPotentialCapture = Boolean(
    selectedSquare && square && availableMoves.includes(square),
  );

  const isFromOriginalLeftHandSide = piecePlayerSide === "w";

  // Determine if piece should face left (towards opposite side)
  const shouldFaceLeft = pieceShouldFaceLeft(boardOrientation, piecePlayerSide);

  const horizontalTranslation = isFromOriginalLeftHandSide
    ? isKnight
      ? "left-2"
      : "left-0"
    : "right-0";

  const verticalTranslation =
    isKnight && isFromOriginalLeftHandSide ? "top-2" : "top-1";

  const classes = [
    "relative",
    isKnight ? "w-10/12" : "w-11/12",
    "aspect-square",
    "bg-no-repeat",
    "bg-cover",
    CHESS_PIECE_Z_INDEXES.character,
    horizontalTranslation,
    verticalTranslation,
    pieceBackgroundClass, // Use Tailwind class instead of inline style
    // Horizontal flip for pieces facing left
    shouldFaceLeft ? "-scale-x-100" : "",
    // Shadow effects based on piece state
    isHighlighted
      ? isPlayable
        ? "drop-shadow-playable-selected-piece"
        : "drop-shadow-non-playable-selected-piece"
      : piecePlayerSide === "w"
        ? "drop-shadow-piece-unit-w"
        : "drop-shadow-piece-unit-b",
    isPotentialCapture ? "drop-shadow-potential-capture" : "",
    ...additionalClasses,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={classes} data-piece-role={pieceRole} />;
};
