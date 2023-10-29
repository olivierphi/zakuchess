import type { ChessSquare } from "business-logic/chess-domain.js"

export const DAILY_CHALLENGE_PATHS = {
  MAIN_PAGE: "/",
  HTMX_SELECT_PIECE: "/htmx/pieces/select",
} as const

export type DailyChallengePath = keyof typeof DAILY_CHALLENGE_PATHS

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type RoutingFunction = (...args: any[]) => string

export const routes: Record<DailyChallengePath, RoutingFunction> = {
  MAIN_PAGE: () => "/",
  HTMX_SELECT_PIECE: ({
    square,
    boardId,
  }: {
    square: ChessSquare
    boardId: string
  }): string => {
    return (
      DAILY_CHALLENGE_PATHS.HTMX_SELECT_PIECE +
      "?" +
      new URLSearchParams({ square: square, boardId: boardId }).toString()
    )
  },
} as const
