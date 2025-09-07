import type {
  BoardOrientation,
  Square,
  PieceRole,
  PlayerSide,
  PieceSymbol,
  PieceName,
  GameFactions,
  ChessFile,
  ChessRank,
} from "./chess-logic.ts";

export function fileAndRankFromSquare(square: Square): [ChessFile, ChessRank] {
  return [square[0] as ChessFile, square[1] as ChessRank];
}

export function pieceNameFromPieceSymbol(pieceType: PieceSymbol): PieceName {
  const pieceTypeToName: Record<PieceSymbol, PieceName> = {
    p: "pawn",
    n: "knight",
    b: "bishop",
    r: "rook",
    q: "queen",
    k: "king",
  };
  return pieceTypeToName[pieceType];
}

export function pieceNameFromPieceRole(pieceRole: PieceRole): PieceName {
  const pieceType = typeFromPieceRole(pieceRole);
  return pieceNameFromPieceSymbol(pieceType);
}

export function playerSideFromPieceRole(pieceRole: PieceRole): PlayerSide {
  return pieceRole.charAt(0).toLowerCase() === pieceRole.charAt(0) ? "b" : "w";
}

export function typeFromPieceRole(pieceRole: PieceRole): PieceSymbol {
  return pieceRole.charAt(0).toLowerCase() as PieceSymbol;
}

export function pieceShouldFaceLeft(
  boardOrientation: BoardOrientation,
  playerSide: PlayerSide,
): boolean {
  if (boardOrientation === "1->8") {
    return playerSide === "b";
  } else {
    return playerSide === "w";
  }
}
