import type {
  BoardOrientation,
  ChessFile,
  ChessRank,
  Square,
} from "./chess-logic.ts";
import { fileAndRankFromSquare } from "./utils.ts";

export const SQUARE_COLOR_TAILWIND_CLASSES = [
  "bg-chess-square-dark",
  "bg-chess-square-light",
] as const;

export const PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: Record<
  string,
  string
> = {
  "w-false": "bg-emerald-800/40 border-2 border-emerald-800",
  "b-false": "bg-indigo-800/40 border-2 border-indigo-800",
  "w-true": "bg-emerald-600/40 border-2 border-emerald-800",
  "b-true": "bg-indigo-600/40 border-2 border-indigo-800",
} as const;

export const CHESS_PIECE_Z_INDEXES = {
  ground_marker: "z-0",
  symbol: "z-10",
  character: "z-20",
} as const;

const PIECE_FILE_TO_TAILWIND_POSITIONING_CLASS: Record<
  BoardOrientation,
  Record<ChessFile, string>
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
  Record<ChessRank, string>
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

// TODO: do we still need these 2 "TAILWIND_POSITIONING_CLASS" mappings?
const SQUARE_FILE_TO_TAILWIND_POSITIONING_CLASS: Record<ChessFile, string> = {
  a: "top-1/8%",
  b: "top-2/8%",
  c: "top-3/8%",
  d: "top-4/8%",
  e: "top-5/8%",
  f: "top-6/8%",
  g: "top-7/8%",
  h: "top-8/8%",
};
const SQUARE_RANK_TO_TAILWIND_POSITIONING_CLASS: Record<ChessRank, string> = {
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
