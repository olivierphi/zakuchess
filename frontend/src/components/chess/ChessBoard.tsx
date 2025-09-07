import React, { type JSX } from "react";
import { type BoardOrientation, type Square } from "@shared/chess/types.ts";
import ChessBoardSquare from "./ChessBoardSquare.tsx";
import { FILE_NAMES, RANK_NAMES } from "@shared/chess/consts.ts";

interface ChessBoardProps {
  boardOrientation: BoardOrientation;
  boardId: string;
  forceSquareInfo?: boolean;
}

const ChessBoard: React.FC<ChessBoardProps> = ({
  boardOrientation,
  boardId,
  forceSquareInfo = false,
}) => {
  const squares: JSX.Element[] = [];

  // Generate squares based on board orientation
  // With 90-degree rotation: iterate ranks then files to match the visual layout
  if (boardOrientation === "1->8") {
    // Rank 1 on left, rank 8 on right; file a on top, file h on bottom
    for (const rank of RANK_NAMES) {
      for (const file of FILE_NAMES) {
        const square = `${file}${rank}` as Square;
        squares.push(
          <ChessBoardSquare
            key={square}
            boardOrientation={boardOrientation}
            square={square}
            forceSquareInfo={forceSquareInfo}
          />,
        );
      }
    }
  } else {
    // Rank 8 on left, rank 1 on right; file h on top, file a on bottom
    for (const rank of [...RANK_NAMES].reverse()) {
      for (const file of [...FILE_NAMES].reverse()) {
        const square = `${file}${rank}` as Square;
        squares.push(
          <ChessBoardSquare
            key={square}
            boardOrientation={boardOrientation}
            square={square}
            forceSquareInfo={forceSquareInfo}
          />,
        );
      }
    }
  }

  const squaresContainerClasses = ["relative", "aspect-square"];
  const boardAttributes: React.CSSProperties = {};

  // Default board texture (can be made configurable later)
  // For now, use plain styling

  return (
    <div
      id={`chess-board-${boardId}`}
      className="pointer-events-none"
      style={boardAttributes}
    >
      <div
        id={`chess-board-squares-${boardId}`}
        className={squaresContainerClasses.join(" ")}
      >
        {squares}
      </div>
    </div>
  );
};

export default ChessBoard;
