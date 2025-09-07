export const FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"] as const;
export const RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"] as const;

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
