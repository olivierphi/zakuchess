import { create } from "zustand";
import { Chess } from "chess.js";
import {
  type Square,
  type PieceStateBySquare,
  type FEN,
} from "@shared/chess/chess-logic.ts";
import { chessBoardToPieceStateBySquare } from "@shared/chess/game-initialisation.ts";

interface ChessGameState {
  fen: string;
  pieceStateBySquare: PieceStateBySquare;
  chess: Chess;
}

interface ChessGameActions {
  initialise: (args: {
    fen: FEN;
    pieceStateBySquare: PieceStateBySquare;
  }) => void;
  getLegalMoves: (square: Square) => Square[];
  makeMove: (from: Square, to: Square) => boolean;
}

export type ChessGameStore = ChessGameState & ChessGameActions;

const DEFAULT_STARTING_FEN =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

export const useChessGameStore = create<ChessGameStore>((set, get) => {
  const fen = DEFAULT_STARTING_FEN;
  const initialChess = new Chess(fen);
  const pieceStateBySquare = chessBoardToPieceStateBySquare(initialChess);

  return {
    fen,
    chess: initialChess,
    pieceStateBySquare,

    initialise: ({
      fen,
      pieceStateBySquare,
    }: {
      fen: FEN;
      pieceStateBySquare: PieceStateBySquare;
    }) => {
      const chess = new Chess(fen);
      set({ fen, chess, pieceStateBySquare });
    },

    getLegalMoves: (square: Square) => {
      const { chess } = get();
      const moves = chess.moves({ square, verbose: true });
      return moves.map((move) => move.to as Square);
    },

    makeMove: (from: Square, to: Square) => {
      // TODO: this should actually trigger a `fetch()` call to the API, and the move done server-side
      const { chess } = get();
      const move = chess.move({ from, to });

      if (move) {
        const fen = chess.fen();
        const pieceStateBySquare = chessBoardToPieceStateBySquare(chess);
        set({ fen, chess, pieceStateBySquare });
        return true;
      }
      return false;
    },
  };
});
