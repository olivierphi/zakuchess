import React from "react";
import type { PlayerSide } from "./types";
import {
  CHESS_PIECE_Z_INDEXES,
  PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES,
} from "./consts.ts";

interface ChessUnitGroundMarkerProps {
  playerSide: PlayerSide;
  canMove?: boolean;
}

const ChessUnitGroundMarker: React.FC<ChessUnitGroundMarkerProps> = ({
  playerSide,
  canMove = false,
}) => {
  const key = `${playerSide}-${canMove}`;
  const colorClass = PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[key];

  const classes = [
    "absolute",
    "w-11/12",
    "h-2/5",
    "left-1/24",
    "bottom-0.5",
    "rounded-oval",
    CHESS_PIECE_Z_INDEXES.ground_marker,
    "border-solid",
    colorClass,
  ].join(" ");

  return <div className={classes} />;
};

export default ChessUnitGroundMarker;
