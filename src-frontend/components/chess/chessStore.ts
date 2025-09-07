import { create } from "zustand";
import { Chess } from "chess.js";
import type { Square, PieceRole } from "./types";

interface ChessGameState {
  fen: string;
  pieceRoleBySquare: Partial<Record<Square, PieceRole>>;
  chess: Chess;
}

interface ChessGameActions {
  setFen: (fen: string) => void;
  getLegalMoves: (square: Square) => Square[];
  makeMove: (from: Square, to: Square) => boolean;
}

export type ChessGameStore = ChessGameState & ChessGameActions;

function chessBoardToPieceRoleBySquare(
  chess: Chess,
): Partial<Record<Square, PieceRole>> {
  const result: Partial<Record<Square, PieceRole>> = {};

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

        let pieceRole: PieceRole;

        if (pieceType === "k") {
          // King is always K/k
          pieceRole = (playerSide === "w" ? "K" : "k") as PieceRole;
        } else if (pieceType === "q") {
          // Queen is always Q/q
          pieceRole = (playerSide === "w" ? "Q" : "q") as PieceRole;
        } else if (pieceType === "p") {
          // Pawns are numbered 1-8
          pieceCounts[playerSide].p++;
          const pawnNumber = pieceCounts[playerSide].p;
          pieceRole = (
            playerSide === "w" ? `P${pawnNumber}` : `p${pawnNumber}`
          ) as PieceRole;
        } else if (pieceType === "r") {
          // Rooks are numbered 1-2
          pieceCounts[playerSide].r++;
          const rookNumber = pieceCounts[playerSide].r;
          pieceRole = (
            playerSide === "w" ? `R${rookNumber}` : `r${rookNumber}`
          ) as PieceRole;
        } else if (pieceType === "n") {
          // Knights are numbered 1-2
          pieceCounts[playerSide].n++;
          const knightNumber = pieceCounts[playerSide].n;
          pieceRole = (
            playerSide === "w" ? `N${knightNumber}` : `n${knightNumber}`
          ) as PieceRole;
        } else if (pieceType === "b") {
          // Bishops are numbered 1-2
          pieceCounts[playerSide].b++;
          const bishopNumber = pieceCounts[playerSide].b;
          pieceRole = (
            playerSide === "w" ? `B${bishopNumber}` : `b${bishopNumber}`
          ) as PieceRole;
        } else {
          // Fallback - should not happen
          pieceRole = `${playerSide}${pieceType}` as PieceRole;
        }

        result[square] = pieceRole;
      }
    });
  });

  return result;
}

const DEFAULT_STARTING_FEN =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

export const useChessGameStore = create<ChessGameStore>((set, get) => {
  const initialChess = new Chess(DEFAULT_STARTING_FEN);

  return {
    fen: DEFAULT_STARTING_FEN,
    chess: initialChess,
    pieceRoleBySquare: chessBoardToPieceRoleBySquare(initialChess),

    setFen: (fen: string) => {
      const chess = new Chess(fen);
      const pieceRoleBySquare = chessBoardToPieceRoleBySquare(chess);
      set({ fen, chess, pieceRoleBySquare });
    },

    getLegalMoves: (square: Square) => {
      const { chess } = get();
      const moves = chess.moves({ square, verbose: true });
      return moves.map((move) => move.to as Square);
    },

    makeMove: (from: Square, to: Square) => {
      const { chess } = get();
      const move = chess.move({ from, to });

      if (move) {
        const fen = chess.fen();
        const pieceRoleBySquare = chessBoardToPieceRoleBySquare(chess);
        set({ fen, chess, pieceRoleBySquare });
        return true;
      }
      return false;
    },
  };
});
