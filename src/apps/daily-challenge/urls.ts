import type { ChessSquare } from "apps/chess/business-logic/chess-domain.js"

export const DAILY_CHALLENGE_PATHS = {
  MAIN_PAGE: "/",
  HTMX_SELECT_PIECE: "/htmx/pieces/select",
  HTMX_MOVE_PIECE: "/htmx/pieces/move",
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
      new URLSearchParams({ square, boardId }).toString()
    )
  },

  HTMX_MOVE_PIECE: ({
    from,
    to,
    boardId,
  }: {
    from: ChessSquare
    to: ChessSquare
    boardId: string
  }): string => {
    return (
      DAILY_CHALLENGE_PATHS.HTMX_MOVE_PIECE +
      "?" +
      new URLSearchParams({ from, to, boardId }).toString()
    )
  },
} as const
