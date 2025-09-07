import React, { type JSX } from "react";
import type { GamePresenter, Square, BoardOrientation } from "./types";
import { squareToPositioningTailwindClasses } from "./utils";

interface ChessLastMoveProps {
  boardId: string;
}

interface ChessLastMoveMarkerProps {
  boardOrientation: BoardOrientation;
  square: Square;
  movePart: "from" | "to";
}

const ChessLastMoveMarker: React.FC<ChessLastMoveMarkerProps> = ({
  boardOrientation,
  square,
  movePart,
}) => {
  const { startClass, targetClass } = (() => {
    switch (movePart) {
      case "from":
        return { startClass: "w-full!", targetClass: "w-3/5" };
      case "to":
        return { startClass: "w-3/5!", targetClass: "w-11/12" };
      default:
        throw new Error(`Invalid movePart: ${movePart}`);
    }
  })();

  const movementMarkerClasses = [
    "aspect-square",
    "bg-sky-300",
    "opacity-70",
    "border",
    "border-sky-500",
    "rounded-full",
    "transition-size",
    "duration-400",
    "ease-in-out",
    "transform-gpu",
    startClass,
    targetClass,
  ].join(" ");

  const movementMarkerContainerClasses = [
    "absolute",
    "aspect-square",
    "w-1/8",
    "flex items-center justify-center",
    ...squareToPositioningTailwindClasses(boardOrientation, square),
  ].join(" ");

  return (
    <div className={movementMarkerContainerClasses}>
      <div className={movementMarkerClasses} data-last-move-marker={movePart} />
    </div>
  );
};

const ChessLastMove: React.FC<ChessLastMoveProps> = ({ boardId }) => {
  // TODO: Implement last move display using store data
  return (
    <div
      className="relative aspect-square pointer-events-none"
      id={`chess-last-move-${boardId}`}
    >
      {/* Last move markers would go here */}
    </div>
  );
};

export default ChessLastMove;
