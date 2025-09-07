import React from "react";

interface ChessBotDataProps {
  boardId: string;
}

const ChessBotData: React.FC<ChessBotDataProps> = ({ boardId }) => {
  // This would contain the chess engine configuration
  const chessEngineUrls = {
    id: "stockfish",
    wasm: "/js/bot/stockfish.wasm.js",
    js: "/js/bot/stockfish.js",
  };

  return (
    <div
      id={`chess-bot-data-${boardId}`}
      aria-hidden="true"
      data-chess-engine-urls={JSON.stringify(chessEngineUrls)}
    />
  );
};

export default ChessBotData;
