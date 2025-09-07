import React, { useMemo } from "react";
import type { BoardOrientation, Square } from "@shared/chess/types.ts";
import {
  fileAndRankFromSquare,
  squareToPositioningTailwindClasses,
} from "@shared/chess/utils.ts";
import {
  FILE_NAMES,
  RANK_NAMES,
  SQUARE_COLOR_TAILWIND_CLASSES,
} from "@shared/chess/consts.ts";

interface ChessBoardSquareProps {
  boardOrientation: BoardOrientation;
  square: Square;
  forceSquareInfo?: boolean;
}

const ChessBoardSquare: React.FC<ChessBoardSquareProps> = React.memo(
  ({ boardOrientation, square, forceSquareInfo = false }) => {
    const [file, rank] = useMemo(() => fileAndRankFromSquare(square), [square]);

    const { squareColorClass, positioningClasses, squareInfo } = useMemo(() => {
      const fileIndex = FILE_NAMES.indexOf(file);
      const rankIndex = RANK_NAMES.indexOf(rank);
      const squareIndex = fileIndex + rankIndex;
      const squareColorClass = SQUARE_COLOR_TAILWIND_CLASSES[squareIndex % 2];

      const positioningClasses = squareToPositioningTailwindClasses(
        boardOrientation,
        square,
      );

      let displayedFile: string | null = null;
      let displayedRank: string | null = null;

      if (forceSquareInfo) {
        displayedFile = file;
        displayedRank = rank;
      } else {
        // With 90-degree rotation: ranks are columns, files are rows
        // Left column shows files, top row shows ranks
        switch (boardOrientation) {
          case "1->8":
            // Show file labels on the leftmost column (rank 1 column)
            if (rank === "1") displayedFile = file;
            // Show rank labels on the top row (file a row)
            if (file === "a") displayedRank = rank;
            break;
          case "8->1":
            // Show file labels on the leftmost column (rank 8 column)
            if (rank === "8") displayedFile = file;
            // Show rank labels on the top row (file h row)
            if (file === "h") displayedRank = rank;
            break;
        }
      }

      const squareInfo =
        displayedFile || displayedRank
          ? `${displayedFile || ""}${displayedRank || ""}`
          : null;

      return { squareColorClass, positioningClasses, squareInfo };
    }, [boardOrientation, square, file, rank, forceSquareInfo]);

    const classes = [
      "absolute",
      "aspect-square",
      "w-1/8",
      squareColorClass,
      ...positioningClasses,
    ].join(" ");

    return (
      <div className={classes} data-square={square}>
        {squareInfo && (
          <span className="text-chess-square-square-info select-none">
            {squareInfo}
          </span>
        )}
      </div>
    );
  },
);

ChessBoardSquare.displayName = "ChessBoardSquare";

export default ChessBoardSquare;
