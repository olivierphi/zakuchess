import type { BoardPieces, Piece, PlayerSide, PossibleMove, Square } from "$lib/domain/chess/types"

import { ChessPiece } from "./ChessPiece"

type ChessPiecesProps = {
	pieces: BoardPieces
	currentSide: PlayerSide
	possibleMoves: PossibleMove[]
	selectedPiece: { square: Square; piece: Piece } | null
	selectedPiecePossibleTargets: Square[] | null
	onPieceSelection: (square: Square, piece: Piece) => void
}

export function ChessPieces(props: ChessPiecesProps) {
	const piecesThatCanMove: Square[] = props.possibleMoves.map((move) => move.from)
	return (
		<div data-unit-type="chess-pieces">
			{Object.entries(props.pieces).map(([sq, piece]) => {
				const square = sq as Square
				const isActivePlayer = piece.side === props.currentSide
				const canMove = piecesThatCanMove.includes(square)
				const key = `${piece.side}-${piece.role}`
				const isPossibleTarget = props.selectedPiecePossibleTargets?.includes(square) ?? false

				return (
					<ChessPiece
						isActivePlayer={isActivePlayer}
						square={square as Square}
						piece={piece}
						canMove={canMove}
						isSelected={props.selectedPiece?.square === square}
						isPossibleTarget={isPossibleTarget}
						onSelect={canMove ? props.onPieceSelection : undefined}
						key={key}
					/>
				)
			})}
		</div>
	)
}
