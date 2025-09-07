import React from "react";
import type {
  BoardOrientation,
  PieceName,
  PieceRole,
  PlayerSide,
} from "@shared/chess/chess-logic.ts";
import {
  playerSideFromPieceRole,
  typeFromPieceRole,
  pieceNameFromPieceRole,
  pieceShouldFaceLeft,
} from "@shared/chess/utils.ts";
import { CHESS_PIECE_Z_INDEXES } from "@shared/chess/chess-html-display.ts";

const PIECE_SYMBOLS_CLASSES: Record<PlayerSide, Record<PieceName, string>> = {
  // We need Tailwind to see these classes, so that it bundles them in the final CSS file.
  w: {
    pawn: "bg-w-pawn",
    knight: "bg-w-knight",
    bishop: "bg-w-bishop",
    rook: "bg-w-rook",
    queen: "bg-w-queen",
    king: "bg-w-king",
  },
  b: {
    pawn: "bg-b-pawn",
    knight: "bg-b-knight",
    bishop: "bg-b-bishop",
    rook: "bg-b-rook",
    queen: "bg-b-queen",
    king: "bg-b-king",
  },
};

interface ChessUnitSymbolDisplayProps {
  boardOrientation: BoardOrientation;
  pieceRole: PieceRole;
}

export const ChessUnitSymbolDisplay: React.FC<ChessUnitSymbolDisplayProps> = ({
  boardOrientation,
  pieceRole,
}) => {
  const playerSide = playerSideFromPieceRole(pieceRole);
  const pieceType = typeFromPieceRole(pieceRole);
  const pieceName = pieceNameFromPieceRole(pieceRole);

  const isKnight = pieceType === "n";
  const isPawn = pieceType === "p";

  const unitSymbolClass = PIECE_SYMBOLS_CLASSES[playerSide][pieceName];

  const symbolClasses = [
    isPawn || isKnight ? "w-7" : "w-8",
    "aspect-square",
    "bg-no-repeat",
    "bg-cover",
    "opacity-90",
    playerSide === "w"
      ? "drop-shadow-piece-symbol-w"
      : "drop-shadow-piece-symbol-b",
    unitSymbolClass,
  ].join(" ");

  const shouldFaceLeft = pieceShouldFaceLeft(boardOrientation, playerSide);

  const symbolDisplayContainerClasses = [
    "absolute",
    "top-0",
    shouldFaceLeft ? "right-0" : "left-0",
    CHESS_PIECE_Z_INDEXES.symbol,
    // Knight facing direction
    isKnight && !shouldFaceLeft ? "-scale-x-100" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={symbolDisplayContainerClasses} data-label={pieceName}>
      <div className={symbolClasses} />
    </div>
  );
};
