import React from "react";
import type { BoardOrientation } from "@shared/chess/chess-logic.ts";
import { ChessArenaProvider } from "./ChessArenaProvider.tsx";
import { ChessLastMove } from "./ChessLastMove.tsx";
import { ChessPieces } from "./ChessPieces.tsx";
import { ChessAvailableTargets } from "./ChessAvailableTargets.tsx";
import { SpeechBubbleContainer } from "./SpeechBubbleContainer.tsx";
import ChessBotData from "./ChessBotData.tsx";

interface ChessArenaDynamicIslandProps {
  initialFen: string;
  boardOrientation: BoardOrientation;
  boardId: string;
}

const ChessArenaDynamicIsland: React.FC<ChessArenaDynamicIslandProps> = ({
  initialFen,
  boardOrientation,
  boardId,
}) => {
  return (
    <ChessArenaProvider initialFen={initialFen}>
      {/* Last move indicators */}
      <div
        className="absolute inset-0 pointer-events-none z-10"
        id={`chess-last-move-container-${boardId}`}
      >
        <ChessLastMove boardId={boardId} />
      </div>

      {/* Chess pieces */}
      <div
        className="absolute inset-0 pointer-events-none z-20"
        id={`chess-pieces-container-${boardId}`}
      >
        <ChessPieces boardId={boardId} />
      </div>

      {/* Available targets */}
      <div
        className="absolute inset-0 pointer-events-none z-30"
        id={`chess-available-targets-container-${boardId}`}
      >
        <ChessAvailableTargets
          boardId={boardId}
          boardOrientation={boardOrientation}
        />
      </div>

      {/* Speech bubbles */}
      <div
        className="absolute inset-0 pointer-events-none z-40"
        id={`chess-speech-container-${boardId}`}
      >
        <SpeechBubbleContainer boardId={boardId} />
      </div>

      {/* Bot data (hidden) */}
      <ChessBotData boardId={boardId} />
    </ChessArenaProvider>
  );
};

export default ChessArenaDynamicIsland;
