import React, { createContext, useContext, useMemo } from "react";
import { create, type StoreApi } from "zustand";
import { Chess } from "chess.js";
import type { Square, PieceRole, Faction } from "@shared/chess/types";

interface ChessGameState {
  fen: string;
  pieceRoleBySquare: Partial<Record<Square, PieceRole>>;
  chess: Chess;
  factions: { w: Faction; b: Faction };
  selectedSquare: Square | null;
  availableMoves: Square[];
  currentPlayer: "w" | "b";
}

interface ChessGameActions {
  setFen: (fen: string) => void;
  getLegalMoves: (square: Square) => Square[];
  makeMove: (from: Square, to: Square) => boolean;
  selectSquare: (square: Square) => void;
  clearSelection: () => void;
}

export type ChessGameStore = ChessGameState & ChessGameActions;
type ChessStoreApi = StoreApi<ChessGameStore>;

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

function createChessArenaStore(initialFen: string): StoreApi<ChessGameStore> {
  return create<ChessGameStore>((set, get) => {
    const initialChess = new Chess(initialFen);

    return {
      fen: initialFen,
      chess: initialChess,
      pieceRoleBySquare: chessBoardToPieceRoleBySquare(initialChess),
      factions: { w: "humans", b: "undead" },
      selectedSquare: null,
      availableMoves: [],
      currentPlayer: initialChess.turn() as "w" | "b",

      setFen: (fen: string) => {
        const chess = new Chess(fen);
        const pieceRoleBySquare = chessBoardToPieceRoleBySquare(chess);
        const currentPlayer = chess.turn() as "w" | "b";
        set({
          fen,
          chess,
          pieceRoleBySquare,
          currentPlayer,
          selectedSquare: null,
          availableMoves: [],
        });
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
          const currentPlayer = chess.turn() as "w" | "b";
          set({
            fen,
            chess,
            pieceRoleBySquare,
            currentPlayer,
            selectedSquare: null,
            availableMoves: [],
          });
          return true;
        }
        return false;
      },

      selectSquare: (square: Square) => {
        const { chess, selectedSquare } = get();

        // If clicking the same square, clear selection
        if (selectedSquare === square) {
          set({ selectedSquare: null, availableMoves: [] });
          return;
        }

        // If there's a piece on this square, select it and show available moves
        const piece = chess.get(square);
        if (piece) {
          const moves = chess.moves({ square, verbose: true });
          const availableMoves = moves.map((move) => move.to as Square);
          set({ selectedSquare: square, availableMoves });
        } else if (selectedSquare) {
          // If clicking an empty square and we have a selection, try to make a move
          const moveSuccessful = get().makeMove(selectedSquare, square);
          if (!moveSuccessful) {
            // Invalid move, clear selection
            set({ selectedSquare: null, availableMoves: [] });
          }
        }
      },

      clearSelection: () => {
        set({ selectedSquare: null, availableMoves: [] });
      },
    };
  });
}

const ChessArenaContext = createContext<StoreApi<ChessGameStore> | null>(null);

interface ChessArenaProviderProps {
  initialFen: string;
  children: React.ReactNode;
}

export const ChessArenaProvider: React.FC<ChessArenaProviderProps> = ({
  initialFen,
  children,
}) => {
  const store = useMemo(() => createChessArenaStore(initialFen), [initialFen]);

  return (
    <ChessArenaContext.Provider value={store}>
      {children}
    </ChessArenaContext.Provider>
  );
};

export function useChessArenaStore<T>(
  selector: (state: ChessGameStore) => T,
): T {
  const store = useContext(ChessArenaContext);
  if (!store) {
    throw new Error(
      "useChessArenaStore must be used within ChessArenaProvider",
    );
  }

  const [state, setState] = React.useState(() => selector(store.getState()));

  React.useEffect(() => {
    const unsubscribe = store.subscribe((newState) => {
      setState(selector(newState));
    });

    return unsubscribe;
  }, [store, selector]);

  return state;
}

export function useChessArenaActions() {
  const store = useContext(ChessArenaContext);
  if (!store) {
    throw new Error(
      "useChessArenaActions must be used within ChessArenaProvider",
    );
  }

  const state = store.getState();
  return {
    setFen: state.setFen,
    getLegalMoves: state.getLegalMoves,
    makeMove: state.makeMove,
    selectSquare: state.selectSquare,
    clearSelection: state.clearSelection,
  };
}
