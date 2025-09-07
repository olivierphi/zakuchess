import type {
  BoardOrientation,
  Square,
  PieceRole,
  PlayerSide,
  PieceType,
  PieceName,
  GameFactions,
} from "./types";
import { FILE_NAMES, RANK_NAMES } from "./consts.ts";

export function fileAndRankFromSquare(square: Square): [string, string] {
  return [square[0], square[1]];
}

export function pieceNameFromPieceType(pieceType: PieceType): PieceName {
  const pieceTypeToName: Record<PieceType, PieceName> = {
    'p': 'pawn',
    'n': 'knight',
    'b': 'bishop',
    'r': 'rook',
    'q': 'queen',
    'k': 'king'
  };
  return pieceTypeToName[pieceType];
}

export function pieceNameFromPieceRole(pieceRole: PieceRole): PieceName {
  const pieceType = typeFromPieceRole(pieceRole);
  return pieceNameFromPieceType(pieceType);
}

export function playerSideFromPieceRole(pieceRole: PieceRole): PlayerSide {
  return pieceRole.charAt(0).toLowerCase() === pieceRole.charAt(0) ? "b" : "w";
}

export function typeFromPieceRole(pieceRole: PieceRole): PieceType {
  return pieceRole.charAt(0).toLowerCase() as PieceType;
}

export function squareToPositioningTailwindClasses(
  boardOrientation: BoardOrientation,
  square: Square,
): string[] {
  const [file, rank] = fileAndRankFromSquare(square);
  const fileIndex = FILE_NAMES.indexOf(file);
  const rankIndex = RANK_NAMES.indexOf(rank);

  let left: number, top: number;

  // 90-degree rotation: ranks become columns, files become rows
  if (boardOrientation === "1->8") {
    // Rank 1 = left column, Rank 8 = right column
    left = rankIndex;
    // File a = top row, File h = bottom row
    top = fileIndex;
  } else {
    // Rank 8 = left column, Rank 1 = right column
    left = 7 - rankIndex;
    // File h = top row, File a = bottom row
    top = 7 - fileIndex;
  }

  const leftClass = `left-${left}/8`;
  const topClass = `top-${top}/8`;

  return [leftClass, topClass];
}

export function chessUnitSymbolClass(
  playerSide: PlayerSide,
  pieceName: string,
): string {
  // This would need to be implemented based on your CSS classes
  return `chess-symbol-${playerSide}-${pieceName}`;
}

export function pieceCharacterClasses(
  boardOrientation: BoardOrientation,
  pieceRole: PieceRole,
  _factions: GameFactions, // TODO!
): string[] {
  // This would need to be implemented based on your faction system
  const playerSide = playerSideFromPieceRole(pieceRole);
  const pieceType = typeFromPieceRole(pieceRole);

  return [`piece-${playerSide}-${pieceType}`];
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
