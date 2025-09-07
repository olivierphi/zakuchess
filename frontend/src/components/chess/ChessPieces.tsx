import React from "react";
import type { Square } from "@shared/chess/types";
import { useChessArenaStore } from "./ChessArenaProvider.tsx";
import ChessPiece from "./ChessPiece.tsx";

interface ChessPiecesProps {
  boardId: string;
}

const ChessPieces: React.FC<ChessPiecesProps> = ({ boardId }) => {
  const { pieceRoleBySquare } = useChessArenaStore((state) => ({
    pieceRoleBySquare: state.pieceRoleBySquare,
  }));

  const piecesToAppend = Object.entries(pieceRoleBySquare).sort(
    ([, roleA], [, roleB]) => roleA.localeCompare(roleB),
  );

  const pieces = piecesToAppend.map(([square, pieceRole]) => (
    <ChessPiece
      key={`${square}-${pieceRole}`}
      square={square as Square}
      pieceRole={pieceRole}
      boardId={boardId}
    />
  ));

  return (
    <div
      id={`chess-board-pieces-${boardId}`}
      className="relative aspect-square"
    >
      {pieces}
    </div>
  );
};

export default ChessPieces;
