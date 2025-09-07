import React from "react";
import type {
  PieceRole,
  Square,
  BoardOrientation,
} from "@shared/chess/chess-logic.ts";
import {
  useChessArenaStore,
  useChessArenaActions,
} from "./ChessArenaProvider.tsx";
import { playerSideFromPieceRole } from "@shared/chess/utils.ts";
import { ChessCharacterDisplay } from "./ChessCharacterDisplay.tsx";
import { ChessUnitSymbolDisplay } from "./ChessUnitSymbolDisplay.tsx";
import { ChessUnitGroundMarker } from "./ChessUnitGroundMarker.tsx";
import { squareToPositioningTailwindClasses } from "@shared/chess/chess-html-display.ts";

interface ChessPieceProps {
  square: Square;
  pieceRole: PieceRole;
  boardId: string;
  boardOrientation?: BoardOrientation;
}

export const ChessPiece: React.FC<ChessPieceProps> = ({
  square,
  pieceRole,
  boardId,
  boardOrientation = "1->8",
}) => {
  const playerSide = playerSideFromPieceRole(pieceRole);
  const { selectSquare } = useChessArenaActions();

  // Get selection state from store
  const { selectedSquare, availableMoves } = useChessArenaStore((state) => ({
    selectedSquare: state.selectedSquare,
    availableMoves: state.availableMoves,
  }));

  const isSelectedPiece = selectedSquare === square;
  const pieceCanBeMovedByPlayer = availableMoves.length > 0 && isSelectedPiece;
  const isGameOver = false; // TODO: get from store if needed

  const classes = [
    "absolute",
    "aspect-square",
    "w-1/8",
    ...squareToPositioningTailwindClasses(boardOrientation, square),
    isGameOver ? "cursor-default" : "cursor-pointer",
    isGameOver ? "pointer-events-none" : "pointer-events-auto",
    // Transition classes
    "transition-coordinates",
    "duration-300",
    "ease-in",
    "transform-gpu",
  ].join(" ");

  const handleClick = () => {
    if (isGameOver) return;

    // Use selectSquare which handles selection logic and move attempts
    selectSquare(square);
  };

  return (
    <button
      className={classes}
      id={`board-${boardId}-side-${playerSide}-piece-${pieceRole}`}
      onClick={handleClick}
      disabled={isGameOver}
      data-square={square}
      data-piece-role={pieceRole}
    >
      <ChessUnitGroundMarker
        playerSide={playerSide}
        canMove={pieceCanBeMovedByPlayer}
      />

      <ChessCharacterDisplay
        pieceRole={pieceRole}
        boardOrientation={boardOrientation}
        square={square}
      />

      <ChessUnitSymbolDisplay
        boardOrientation={boardOrientation}
        pieceRole={pieceRole}
      />
    </button>
  );
};
