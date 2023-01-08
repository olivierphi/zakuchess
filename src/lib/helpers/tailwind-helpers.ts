import { PIECE_ID_TO_NAME } from "$lib/domain/chess/consts"
import type { File, Piece, PieceSymbol, Rank, Square } from "$lib/domain/chess/types.js"

const FILE_TO_TAILWIND_POSITIONING_CLASS: Record<File, string> = {
	a: "translate-y-0/1",
	b: "translate-y-1/1",
	c: "translate-y-2/1",
	d: "translate-y-3/1",
	e: "translate-y-4/1",
	f: "translate-y-5/1",
	g: "translate-y-6/1",
	h: "translate-y-7/1",
}
const RANK_TO_TAILWIND_POSITIONING_CLASS: Record<Rank, string> = {
	1: "translate-x-0/1",
	2: "translate-x-1/1",
	3: "translate-x-2/1",
	4: "translate-x-3/1",
	5: "translate-x-4/1",
	6: "translate-x-5/1",
	7: "translate-x-6/1",
	8: "translate-x-7/1",
}

export const squareToTailwindClasses = (square: Square): string[] => {
	const [file, rank] = [square[0] as File, square[1] as Rank]
	return [FILE_TO_TAILWIND_POSITIONING_CLASS[file], RANK_TO_TAILWIND_POSITIONING_CLASS[rank]]
}

export const pieceToTailwindClasses = (piece: Piece): string[] => {
	const pieceId = piece.role[0] as PieceSymbol
	const classes = [`bg-wesnoth-loyalists-${PIECE_ID_TO_NAME[pieceId]}`]
	if (piece.side === "b") {
		classes.push("-scale-x-100")
	}
	return classes
}
