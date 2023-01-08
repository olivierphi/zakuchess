import { fenToGameState } from "$lib/domain/chess/chess-helpers"
import { FEN_NEW_GAME } from "$lib/domain/chess/consts"
import type { FEN, Piece, Square } from "$lib/domain/chess/types"
import { useCallback, useState } from "react"

import { ChessBoardBackground } from "./ChessBoardBackground"
import { ChessPieces } from "./ChessPieces"
import { ChessPotentialTargets } from "./ChessPotentialTargets"

type ChessArenaProps = {
	fen?: FEN
}

export function ChessArena(props: ChessArenaProps) {
	const [selectedPiece, setSelectedPiece] = useState<{ square: Square; piece: Piece } | null>(null)

	// END OF HOOKS

	const fen = props.fen || FEN_NEW_GAME
	// State derived from props:
	const { currentSide, pieces, possibleMoves } = fenToGameState(fen)
	const selectedPiecePossibleTargets: Square[] | null =
		selectedPiece && possibleMoves.length > 0
			? possibleMoves.filter(({ from }) => from === selectedPiece.square).map(({ to }) => to)
			: null

	// Callbacks:
	const onPieceSelection = useCallback(
		(square: Square, piece: Piece): void => {
			setSelectedPiece({ square, piece })
		},
		[setSelectedPiece],
	)
	const onTargetSelection = useCallback(
		(square: Square): void => {
			console.log("onTargetSelection()", square)
			// TODO: backend logic call
		},
		[selectedPiece],
	)

	return (
		<div className="w-full md:max-w-xl mx-auto aspect-square relative ">
			<div className="absolute inset-0 z-0 pointer-events-none">
				<ChessBoardBackground />
			</div>
			<div className="absolute inset-0 z-10">
				<ChessPieces
					pieces={pieces}
					currentSide={currentSide}
					possibleMoves={possibleMoves}
					onPieceSelection={onPieceSelection}
					selectedPiece={selectedPiece}
					selectedPiecePossibleTargets={selectedPiecePossibleTargets}
				/>
			</div>
			<div className="absolute inset-0 z-20 pointer-events-none">
				<ChessPotentialTargets
					selectedPiecePossibleTargets={selectedPiecePossibleTargets}
					onTargetSelection={onTargetSelection}
				/>
			</div>
		</div>
	)
}
