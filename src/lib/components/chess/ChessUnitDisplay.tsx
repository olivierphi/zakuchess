import type { Piece } from "$lib/domain/chess/types"
import { pieceToTailwindClasses } from "$lib/helpers/tailwind-helpers"

type ChessUnitDisplayProps = {
	piece: Piece
	isActivePlayer: boolean
	isSelected: boolean
	isPossibleTarget: boolean
}

export function ChessUnitDisplay(props: ChessUnitDisplayProps) {
	const classes = [
		"relative",
		"w-full",
		"aspect-square",
		"bg-no-repeat",
		"bg-cover",
		"z-10",
		...pieceToTailwindClasses(props.piece),
		// Conditional classes:
		props.isSelected ? "drop-shadow-selected-piece" : "",
		props.isPossibleTarget ? "drop-shadow-potential-capture" : "",
	]
	return <div data-unit-type="piece-display" className={classes.join(" ")} />
}
