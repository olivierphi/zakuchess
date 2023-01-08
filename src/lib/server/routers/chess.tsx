import { chessRepository } from "$lib/server/db/repositories/chess-repository"
import type { ChessEntity } from "$lib/server/db/repositories/chess-repository"
import { z } from "zod"

import { publicProcedure, router } from "../trpc"

export const chessRouter = router({
	createNewGame: publicProcedure
		.input(
			z.object({
				botSide: z.optional(z.enum(["w", "b"])),
			}),
		)
		.mutation(async ({ input }): Promise<ChessEntity> => {
			const newGame = await chessRepository.createNewGame(input.botSide)
			return newGame
		}),
})
