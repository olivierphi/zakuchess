import { type ReactNode, memo } from "react"

import {
    type ChessSquare,
    type FEN,
    FILE_NAMES,
    RANK_NAMES,
    SQUARES,
} from "~/business-logic/chess/chess.domain"
import { squareToFileAndRank } from "~/business-logic/chess/chess.helpers"

import { squareToPieceTailwindClasses } from "./chess-components.helpers"

const _CHESS_PIECE_Z_INDEXES: Record<string, string> = {
    // N.B. z-indexes must be multiples of 10 in Tailwind.
    ground_marker: "z-0",
    symbol: "z-10",
    character: "z-20",
} as const

const _SQUARE_COLOR_TAILWIND_CLASSES = [
    "bg-chess-square-dark",
    "bg-chess-square-light",
] as const

export type ChessBoardProps = {
    boardId: string
}

export function ChessBoard({ boardId }: ChessBoardProps) {
    return (
        <div
            className="relative aspect-square pointer-events-none"
            id={`chess-board-${boardId}`}
        >
            {SQUARES.map((square) => {
                return <ChessBoardSquare key={square} square={square} />
            })}
        </div>
    )
}

type ChessBoardSquareProps = {
    square: ChessSquare
    forceSquareInfo?: boolean
}

const ChessBoardSquare = memo(function ChessBoardSquare({
    square,
    forceSquareInfo,
}: ChessBoardSquareProps) {
    const [file, rank] = squareToFileAndRank(square)
    const squareIndex = FILE_NAMES.indexOf(file) + RANK_NAMES.indexOf(rank)
    const squareColorClass = _SQUARE_COLOR_TAILWIND_CLASSES[squareIndex % 2]
    const classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        squareColorClass,
        ...squareToPieceTailwindClasses(square),
    ]

    const displaySquareInfo: boolean = forceSquareInfo || file == "a" || rank == "1"
    let squareInfo: ReactNode = undefined
    if (displaySquareInfo) {
        const squareName = forceSquareInfo
            ? `${file}${rank}`
            : [rank == "1" ? file : "", file == "a" ? rank : ""].join("")
        squareInfo = <span className="text-chess-square-square-info">{squareName}</span>
    }

    // N.B. `data-square` is mostly for debugging purposes
    return (
        <div className={classes.join(" ")} data-square={square}>
            {squareInfo}
        </div>
    )
})
