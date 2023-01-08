import { FEN_NEW_GAME } from "$lib/domain/chess/consts"
import type { PlayerSide } from "$lib/domain/chess/types"
import { pg } from "$lib/server/db/db-driver"

import type { ChessEntity, ChessRepository } from "./chess-repository"

type ChessEntityRaw = {
	id: number // TODO: manage public ids
	fen: string
	bot_side?: string
}

export class ChessRepositoryCockroachDB implements ChessRepository {
	async createNewGame(botSide?: PlayerSide): Promise<ChessEntity> {
		const result = await pg<ChessEntityRaw>("games").insert(
			{
				fen: FEN_NEW_GAME,
				bot_side: botSide,
			},
			["id", "fen", "bot_side"],
		)

		const firstRow = result[0]
		return {
			id: firstRow.id.toString(),
			fen: firstRow.fen,
			botSide: firstRow.bot_side as PlayerSide,
		}
	}
}
