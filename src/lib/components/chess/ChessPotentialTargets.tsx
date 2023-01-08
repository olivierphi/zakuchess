import type { Square } from "$lib/domain/chess/types"
import { squareToTailwindClasses } from "$lib/helpers/tailwind-helpers"

type ChessPotentialTargetsProps = {
	selectedPiecePossibleTargets: Square[] | null
	onTargetSelection: (target: Square) => void
}

export function ChessPotentialTargets(props: ChessPotentialTargetsProps) {
	return (
		<div data-unit-type="potential-targets" className="relative aspect-square pointer-events-none">
			{props.selectedPiecePossibleTargets?.map((square) => (
				<PotentialTargetMarker square={square} onTargetSelection={props.onTargetSelection} key={square} />
			))}
		</div>
	)
}

// N.B. We might extract this internal component to a proper standalone one later one if needed:

type PotentialTargetMarkerProps = {
	square: Square
	onTargetSelection: (target: Square) => void
}

function PotentialTargetMarker(props: PotentialTargetMarkerProps) {
	const targetMarker = (
		<div className="w-1/5 h-1/5 rounded-full bg-chess-selection transition-size hover:w-1/4 hover:h-1/4 " />
	)
	const targetMarkerContainer = (
		<div className="w-full aspect-square flex items-center justify-center">{targetMarker}</div>
	)
	const classes = [
		"absolute",
		"aspect-square",
		"w-1/8",
		...squareToTailwindClasses(props.square),
		"cursor-pointer",
		"pointer-events-auto",
	]
	return (
		<div
			data-unit-type="potential-target-marker"
			className={classes.join(" ")}
			onClick={() => props.onTargetSelection(props.square)}
		>
			{targetMarkerContainer}
		</div>
	)
}
