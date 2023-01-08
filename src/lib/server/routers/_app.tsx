import { router } from "../trpc"
import { chessRouter } from "./chess"

export const appRouter = router({
	chess: chessRouter, // put procedures under "chess" namespace
})
export type AppRouter = typeof appRouter
