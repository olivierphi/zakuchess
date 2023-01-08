import type { Piece, Square } from "$lib/domain/chess/types"
import { squareToTailwindClasses } from "$lib/helpers/tailwind-helpers"

import { ChessUnitDisplay } from "./ChessUnitDisplay"
import { ChessUnitGroundMarker } from "./ChessUnitGroundMarker"

type ChessPieceProps = {
	square: Square
	piece: Piece
	isActivePlayer: boolean
	isSelected: boolean
	canMove: boolean
	isPossibleTarget: boolean
	onSelect?: (square: Square, piece: Piece) => void
}

export function ChessPiece(props: ChessPieceProps) {
	const classes = [
		"absolute",
		"aspect-square",
		"w-1/8",
		...squareToTailwindClasses(props.square),
		"transition-coordinates",
		"duration-200",
		"ease-in",
		"pointer-events-auto",
		// Conditional classes:
		props.canMove ? "cursor-pointer" : "",
	]

	return (
		<div
			data-unit-type="piece"
			data-square={props.square}
			data-side={props.piece.side}
			data-role={props.piece.role}
			className={classes.join(" ")}
			onClick={props.onSelect ? () => props.onSelect!(props.square, props.piece) : undefined}
		>
			<ChessUnitGroundMarker playerSide={props.piece.side} canMove={props.canMove} />
			<ChessUnitDisplay
				piece={props.piece}
				isActivePlayer={props.isActivePlayer}
				isSelected={props.isSelected}
				isPossibleTarget={props.isPossibleTarget}
			/>
		</div>
	)
}
