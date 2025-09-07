import React from "react";
import type { Square, BoardOrientation } from "@shared/chess/types";
import { useChessArenaStore, useChessArenaActions } from "./ChessArenaProvider";
import { squareToPositioningTailwindClasses } from "@shared/chess/utils";

interface ChessAvailableTargetsProps {
  boardId: string;
  boardOrientation: BoardOrientation;
}

interface ChessAvailableTargetProps {
  square: Square;
  boardOrientation: BoardOrientation;
  boardId: string;
}

const ChessAvailableTarget: React.FC<ChessAvailableTargetProps> = ({
  square,
  boardOrientation,
  boardId: _boardId,
}) => {
  const { selectSquare } = useChessArenaActions();

  // For now, all moves are playable (we can add game state logic later)
  const canMove = true;
  const bgClass = canMove
    ? "bg-playable-chess-available-target-marker"
    : "bg-non-playable-chess-available-target-marker";

  const hoverClass = canMove ? "hover:w-1/3 hover:h-1/3" : "";
  const targetMarkerSize = "w-1/5 h-1/5"; // Simplified for now

  const classes = [
    "absolute",
    "aspect-square",
    "w-1/8",
    "block",
    ...squareToPositioningTailwindClasses(boardOrientation, square),
    canMove ? "cursor-pointer" : "pointer-events-none",
    canMove ? "pointer-events-auto" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const handleClick = () => {
    if (!canMove) return;
    selectSquare(square);
  };

  return (
    <button
      className={classes}
      onClick={handleClick}
      disabled={!canMove}
      data-square={square}
    >
      <div className="w-full aspect-square flex items-center justify-center">
        <div
          className={`${targetMarkerSize} rounded-full transition-all duration-200 ${bgClass} ${hoverClass}`}
        />
      </div>
    </button>
  );
};

const ChessAvailableTargets: React.FC<ChessAvailableTargetsProps> = ({
  boardId,
  boardOrientation,
}) => {
  const { availableMoves } = useChessArenaStore((state) => ({
    availableMoves: state.availableMoves,
  }));

  return (
    <div
      className="relative aspect-square pointer-events-none"
      id={`chess-board-available-targets-${boardId}`}
    >
      {availableMoves.map((square) => (
        <ChessAvailableTarget
          key={square}
          square={square}
          boardOrientation={boardOrientation}
          boardId={boardId}
        />
      ))}
    </div>
  );
};

export default ChessAvailableTargets;
