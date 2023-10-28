import type { ChessSquare } from "business-logic/chess-domain.js"

export const DAILY_CHALLENGE_PATHS = {
  "main-page": "/",
  "htmx:select-piece": "/htmx/pieces/select",
} as const

export type DailyChallengePath = keyof typeof DAILY_CHALLENGE_PATHS

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type RoutingFunction = (...args: any[]) => string

export const routes: Record<DailyChallengePath, RoutingFunction> = {
  "main-page": () => "/",
  "htmx:select-piece": ({
    square,
    boardId,
  }: {
    square: ChessSquare
    boardId: string
  }): string => {
    return (
      "/htmx/pieces/select?" +
      new URLSearchParams({ square: square, boardId: boardId }).toString()
    )
  },
} as const
