import type { FEN, PlayerSide } from "$lib/domain/chess/types"

import { ChessRepositoryCockroachDB } from "./chess-repository.cockroachdb"

export const chessRepository: ChessRepository = new ChessRepositoryCockroachDB()

export interface ChessRepository {
	createNewGame: (botSide?: PlayerSide) => Promise<ChessEntity>
}

export type EntityID = string

export type ChessEntity = {
	id: EntityID
	fen: FEN
	botSide?: PlayerSide
}
