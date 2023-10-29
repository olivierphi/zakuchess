import type { ChessSquare, PieceState } from "apps/chess/business-logic/chess-domain.js"
import { getActivePlayerSideFromFen } from "apps/chess/business-logic/chess-helpers.js"
import { applyChessMove } from "apps/chess/services/applyChessMove.js"
import type { PlayerGameState } from "../business-logic/domain.js"

type MoveDailyChallengePieceArgs = {
  gameState: PlayerGameState
  from: ChessSquare
  to: ChessSquare
  isMySide: boolean
}

export const moveDailyChallengePiece = async ({
  gameState,
  from,
  to,
  isMySide, //eslint-disable-line @typescript-eslint/no-unused-vars
}: MoveDailyChallengePieceArgs): Promise<
  [newGameState: PlayerGameState, capturedPiece: PieceState | null]
> => {
  const fen = gameState.fen
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const activePlayerSide = getActivePlayerSideFromFen(fen)
  try {
    applyChessMove({ fen, from, to })
  } catch (error) {
    throw new Error(
      `An error occurred while trying to move a piece from ${from} to ${to} for FEN '${fen}': ${error}`,
    )
  }

  // TODO: finish this function
  return [gameState, null]
}
