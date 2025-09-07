import type { PieceID, PieceStateBySquare, Square } from "./chess-logic.ts";
import type { Chess } from "chess.js";

export function chessBoardToPieceStateBySquare(
  chess: Chess,
): PieceStateBySquare {
  const result: Partial<Record<Square, PieceID>> = {};

  // Get the board representation from chess.js
  const board = chess.board();

  // Convert chess.js board format to our pieceRoleBySquare format
  const files = ["a", "b", "c", "d", "e", "f", "g", "h"];

  // Track piece counts for numbering
  const pieceCounts = {
    w: { p: 0, n: 0, b: 0, r: 0 },
    b: { p: 0, n: 0, b: 0, r: 0 },
  };

  board.forEach((rank, rankIndex) => {
    rank.forEach((piece, fileIndex) => {
      if (piece) {
        const square = `${files[fileIndex]}${8 - rankIndex}` as Square;
        const playerSide = piece.color; // 'w' or 'b'
        const pieceType = piece.type; // 'p', 'n', 'b', 'r', 'q', 'k'

        let pieceId: PieceID;

        if (pieceType === "k") {
          // King is always K/k
          pieceId = (playerSide === "w" ? "K" : "k") as PieceID;
        } else if (pieceType === "q") {
          // Queen is always Q/q
          pieceId = (playerSide === "w" ? "Q" : "q") as PieceID;
        } else if (pieceType === "p") {
          // Pawns are numbered 1-8
          pieceCounts[playerSide].p++;
          const pawnNumber = pieceCounts[playerSide].p;
          pieceId = (
            playerSide === "w" ? `P${pawnNumber}` : `p${pawnNumber}`
          ) as PieceID;
        } else if (pieceType === "r") {
          // Rooks are numbered 1-2
          pieceCounts[playerSide].r++;
          const rookNumber = pieceCounts[playerSide].r;
          pieceId = (
            playerSide === "w" ? `R${rookNumber}` : `r${rookNumber}`
          ) as PieceID;
        } else if (pieceType === "n") {
          // Knights are numbered 1-2
          pieceCounts[playerSide].n++;
          const knightNumber = pieceCounts[playerSide].n;
          pieceId = (
            playerSide === "w" ? `N${knightNumber}` : `n${knightNumber}`
          ) as PieceID;
        } else if (pieceType === "b") {
          // Bishops are numbered 1-2
          pieceCounts[playerSide].b++;
          const bishopNumber = pieceCounts[playerSide].b;
          pieceId = (
            playerSide === "w" ? `B${bishopNumber}` : `b${bishopNumber}`
          ) as PieceID;
        } else {
          // Fallback - should not happen
          pieceId = `${playerSide}${pieceType}` as PieceID;
        }

        result[square] = pieceId;
      }
    });
  });

  return result;
}
