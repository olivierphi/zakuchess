import { isNotNull } from "$lib/helpers/ts-type-predicates"
import { Move as ChessMove, Chess as ChessObject } from "chess.js"
import LRU from "lru-cache"

import { PIECES_ROLE_BY_STARTING_SQUARE } from "./consts"
import type { BoardPieces, FEN, PlayerSide, PossibleMove, Square } from "./types"

const fenToChessObjectCache = new LRU<FEN, ChessObject>({ max: 50 })

export function fenToChessObject(fen: FEN): ChessObject {
	const cachedObject = fenToChessObjectCache.get(fen)
	if (cachedObject) {
		return cachedObject
	}
	const chessObject = new ChessObject(fen)
	fenToChessObjectCache.set(fen, chessObject)
	return chessObject
}

export type GameState = {
	currentSide: PlayerSide
	pieces: BoardPieces
	possibleMoves: PossibleMove[]
}

export function fenToGameState(fen: FEN): GameState {
	const chessObject = fenToChessObject(fen)
	return {
		currentSide: chessObject.turn(),
		pieces: chessObjectToChessPieces(chessObject),
		possibleMoves: chessObjectToPossibleMoves(chessObject),
	}
}

export function chessObjectToChessPieces(chessObject: ChessObject): BoardPieces {
	return Object.fromEntries(
		chessObject
			.board()
			.flat()
			.filter(isNotNull)
			.map(({ square, type, color }) => {
				return [
					square,
					{
						role: PIECES_ROLE_BY_STARTING_SQUARE[square],
						faction: "wesnoth-loyalists", //TODO: handle factions :-)
						piece: type,
						side: color,
					},
				]
			}),
	)
}

export function chessObjectToPossibleMoves(chessObject: ChessObject): PossibleMove[] {
	return (chessObject.moves({ verbose: true }) as ChessMove[]).map((move) => {
		return {
			side: move.color,
			from: move.from as Square,
			to: move.to as Square,
			piece: move.piece,
			captured: move.captured,
		}
	})
}
