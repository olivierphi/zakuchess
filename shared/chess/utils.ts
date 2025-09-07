import type {
  BoardOrientation,
  Square,
  PieceRole,
  PlayerSide,
  PieceType,
  PieceName,
  GameFactions,
  File,
  Rank,
} from "./types.ts";
import { FILE_NAMES, RANK_NAMES } from "./consts.ts";

export function fileAndRankFromSquare(square: Square): [File, Rank] {
  return [square[0] as File, square[1] as Rank];
}

export function pieceNameFromPieceType(pieceType: PieceType): PieceName {
  const pieceTypeToName: Record<PieceType, PieceName> = {
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
  return pieceNameFromPieceType(pieceType);
}

export function playerSideFromPieceRole(pieceRole: PieceRole): PlayerSide {
  return pieceRole.charAt(0).toLowerCase() === pieceRole.charAt(0) ? "b" : "w";
}

export function typeFromPieceRole(pieceRole: PieceRole): PieceType {
  return pieceRole.charAt(0).toLowerCase() as PieceType;
}

const PIECE_FILE_TO_TAILWIND_POSITIONING_CLASS: Record<
  BoardOrientation,
  Record<File, string>
> = {
  "1->8": {
    a: "translate-y-0/1",
    b: "translate-y-1/1",
    c: "translate-y-2/1",
    d: "translate-y-3/1",
    e: "translate-y-4/1",
    f: "translate-y-5/1",
    g: "translate-y-6/1",
    h: "translate-y-7/1",
  },
  "8->1": {
    a: "translate-y-7/1",
    b: "translate-y-6/1",
    c: "translate-y-5/1",
    d: "translate-y-4/1",
    e: "translate-y-3/1",
    f: "translate-y-2/1",
    g: "translate-y-1/1",
    h: "translate-y-0/1",
  },
};
const PIECE_RANK_TO_TAILWIND_POSITIONING_CLASS: Record<
  BoardOrientation,
  Record<Rank, string>
> = {
  "1->8": {
    "1": "translate-x-0/1",
    "2": "translate-x-1/1",
    "3": "translate-x-2/1",
    "4": "translate-x-3/1",
    "5": "translate-x-4/1",
    "6": "translate-x-5/1",
    "7": "translate-x-6/1",
    "8": "translate-x-7/1",
  },
  "8->1": {
    "1": "translate-x-7/1",
    "2": "translate-x-6/1",
    "3": "translate-x-5/1",
    "4": "translate-x-4/1",
    "5": "translate-x-3/1",
    "6": "translate-x-2/1",
    "7": "translate-x-1/1",
    "8": "translate-x-0/1",
  },
};

const SQUARE_FILE_TO_TAILWIND_POSITIONING_CLASS: Record<File, string> = {
  a: "top-1/8%",
  b: "top-2/8%",
  c: "top-3/8%",
  d: "top-4/8%",
  e: "top-5/8%",
  f: "top-6/8%",
  g: "top-7/8%",
  h: "top-8/8%",
};
const SQUARE_RANK_TO_TAILWIND_POSITIONING_CLASS: Record<Rank, string> = {
  "1": "left-1/8%",
  "2": "left-2/8%",
  "3": "left-3/8%",
  "4": "left-4/8%",
  "5": "left-5/8%",
  "6": "left-6/8%",
  "7": "left-7/8%",
  "8": "left-8/8%",
};

export function squareToPositioningTailwindClasses(
  boardOrientation: BoardOrientation,
  square: Square,
): string[] {
  const [file, rank] = fileAndRankFromSquare(square);
  return [
    PIECE_FILE_TO_TAILWIND_POSITIONING_CLASS[boardOrientation][file],
    PIECE_RANK_TO_TAILWIND_POSITIONING_CLASS[boardOrientation][rank],
  ];
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
