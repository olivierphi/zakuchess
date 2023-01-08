import type { PlayerSide } from "$lib/domain/chess/types"

type ChessUnitGroundMarkerProps = {
	playerSide: PlayerSide
	canMove: boolean
}

const PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: Readonly<Record<string, string>> = {
	"w-cannotMove": "bg-slate-100/40 border border-slate-100",
	"b-cannotMove": "bg-slate-800/40 border border-slate-800",
	"w-canMove": "bg-slate-100/40 border-2 border-chess-selection",
	"b-canMove": "bg-slate-800/40 border-2 border-chess-selection",
}

export function ChessUnitGroundMarker(props: ChessUnitGroundMarkerProps) {
	const markerColorKey = `${props.playerSide}-${props.canMove ? "can" : "cannot"}Move`
	const classes = [
		"absolute",
		"w-5/6",
		"h-1/3",
		"left-1/12",
		"bottom-1",
		"rounded-1/2",
		"z-0",
		"border-solid",
		PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[markerColorKey],
	]
	return <div data-unit-type="ground-marker" className={classes.join(" ")} />
}
