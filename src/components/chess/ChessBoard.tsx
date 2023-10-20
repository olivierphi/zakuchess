import { FC, memo } from "hono/jsx"
import { FILE_NAMES, RANK_NAMES, SQUARES } from "business-logic/chess-domain.js"
import type { ChessSquare } from "business-logic/chess-domain.js"
import { squareToFileAndRank } from "business-logic/chess-helpers.js"
import { squareToPieceTailwindClasses } from "components/chess-components-helpers.js"

export const CHESS_PIECE_Z_INDEXES: Record<string, string> = {
  // N.B. z-indexes must be multiples of 10 in Tailwind.
  ground_marker: "z-0",
  symbol: "z-10",
  character: "z-20",
} as const

const SQUARE_COLOR_TAILWIND_CLASSES = [
  "bg-chess-square-dark",
  "bg-chess-square-light",
] as const

export type ChessBoardProps = {
  boardId: string
}

export const ChessBoard: FC<ChessBoardProps> = memo(({ boardId }) => {
  return (
    <div class="relative aspect-square pointer-events-none" id={`chess-board-${boardId}`}>
      {SQUARES.map((square) => {
        return <ChessBoardSquare square={square} />
      })}
    </div>
  )
})

type ChessBoardSquareProps = {
  square: ChessSquare
  forceSquareInfo?: boolean
}

const ChessBoardSquare: FC<ChessBoardSquareProps> = memo((props) => {
  const [file, rank] = squareToFileAndRank(props.square)
  const squareIndex = FILE_NAMES.indexOf(file) + RANK_NAMES.indexOf(rank)
  const squareColorClass = SQUARE_COLOR_TAILWIND_CLASSES[squareIndex % 2]
  const classes = [
    "absolute",
    "aspect-square",
    "w-1/8",
    squareColorClass,
    ...squareToPieceTailwindClasses(props.square),
  ]

  const displaySquareInfo: boolean = props.forceSquareInfo || file == "a" || rank == "1"
  let squareInfo = ""
  if (displaySquareInfo) {
    const squareName = props.forceSquareInfo
      ? `${file}${rank}`
      : [rank == "1" ? file : "", file == "a" ? rank : ""].join("")
    squareInfo = <span class="text-chess-square-square-info">{squareName}</span>
  }

  // N.B. `data-square` is mostly for debugging purposes
  return (
    <div class={classes.join(" ")} data-square={props.square}>
      {squareInfo}
    </div>
  )
})
