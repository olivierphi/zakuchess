import React from "react";
import type { PieceRole, Square, BoardOrientation } from "./types";
import { useChessArenaStore, useChessArenaActions } from "./ChessArenaProvider";
import {
  playerSideFromPieceRole,
  squareToPositioningTailwindClasses,
} from "./utils";
import ChessCharacterDisplay from "./ChessCharacterDisplay";
import ChessUnitSymbolDisplay from "./ChessUnitSymbolDisplay";
import ChessUnitGroundMarker from "./ChessUnitGroundMarker";

interface ChessPieceProps {
  square: Square;
  pieceRole: PieceRole;
  boardId: string;
  boardOrientation?: BoardOrientation;
}

const ChessPiece: React.FC<ChessPieceProps> = ({
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

export default ChessPiece;
