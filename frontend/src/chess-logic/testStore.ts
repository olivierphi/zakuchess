// Simple test utility for the chess store
import { useChessGameStore } from "./chessStore";

export function testChessStore() {
  console.log("Testing Chess Store with chess.js...");

  // Test with starting position
  const store = useChessGameStore.getState();
  console.log("Starting FEN:", store.fen);
  console.log("Number of pieces:", Object.keys(store.pieceRoleBySquare).length);
  console.log("Sample pieces:", {
    a1: store.pieceRoleBySquare["a1"], // Should be 'wr' (white rook)
    e1: store.pieceRoleBySquare["e1"], // Should be 'wk' (white king)
    e8: store.pieceRoleBySquare["e8"], // Should be 'bk' (black king)
    a8: store.pieceRoleBySquare["a8"], // Should be 'br' (black rook)
    a2: store.pieceRoleBySquare["a2"], // Should be 'wp' (white pawn)
    a7: store.pieceRoleBySquare["a7"], // Should be 'bp' (black pawn)
  });

  // Test legal moves functionality
  console.log("\nTesting legal moves:");
  const pawnMoves = store.getLegalMoves("e2");
  console.log("Legal moves for e2 pawn:", pawnMoves); // Should be ['e3', 'e4']

  const knightMoves = store.getLegalMoves("b1");
  console.log("Legal moves for b1 knight:", knightMoves); // Should be ['a3', 'c3']

  // Test making a move
  console.log("\nTesting makeMove:");
  const moveSuccess = store.makeMove("e2", "e4");
  console.log("Move e2-e4 successful:", moveSuccess);
  console.log("New FEN after e2-e4:", store.fen);

  // Test legal moves after the move
  const newKnightMoves = store.getLegalMoves("b1");
  console.log("Legal moves for b1 knight after e2-e4:", newKnightMoves); // Should include more squares

  // Test with a different position (scholar's mate setup)
  const scholarsMate =
    "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4";
  store.setFen(scholarsMate);
  console.log("\nAfter setting scholar's mate FEN:");
  console.log("New FEN:", store.fen);
  console.log("Number of pieces:", Object.keys(store.pieceRoleBySquare).length);
  console.log("Sample pieces:", {
    c4: store.pieceRoleBySquare["c4"], // Should be 'wb' (white bishop)
    f6: store.pieceRoleBySquare["f6"], // Should be 'bn' (black knight)
    e5: store.pieceRoleBySquare["e5"], // Should be 'bp' (black pawn)
    e4: store.pieceRoleBySquare["e4"], // Should be 'wp' (white pawn)
  });

  // Test bishop legal moves in this position
  const bishopMoves = store.getLegalMoves("c4");
  console.log("Legal moves for c4 bishop:", bishopMoves);

  return {
    success: true,
    message: "Store test with chess.js completed successfully",
  };
}
