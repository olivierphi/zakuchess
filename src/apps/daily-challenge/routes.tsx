import { Hono } from "hono"
import { ChessSquare } from "apps/chess/business-logic/chess-domain.js"
import { getActivePlayerSideFromFen } from "apps/chess/business-logic/chess-helpers.js"
import { ChessArena } from "apps/chess/components/ChessArena.js"
import { Layout } from "apps/chess/components/layout/Layout.js"
import { getCurrentDailyChallengeOrAdminPreview } from "../../http/controller-helpers.js"
import { getOrCreateDailyChallengeStateForPlayer } from "../../http/cookie-helpers.js"
import { logger } from "../../logging.js"
import { DailyChallengeGamePresenter } from "./business-logic/presenters.js"
import { DailyChallengeMovingPartsFragment } from "./components/DailyChallengeMovingPartsFragment.js"
import { moveDailyChallengePiece } from "./services/moveDailyChallengePiece.js"
import { DAILY_CHALLENGE_PATHS, routes } from "./urls.js"

export const dailyChallengeApp = new Hono()

dailyChallengeApp.get(DAILY_CHALLENGE_PATHS.MAIN_PAGE, async (c) => {
  const [challenge, isPreview] = await getCurrentDailyChallengeOrAdminPreview(c.req)
  const boardId = "main" //hard-coded for now
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [gameState, created] = await getOrCreateDailyChallengeStateForPlayer({
    c,
    challenge,
  })
  const gamePresenter = new DailyChallengeGamePresenter({
    challenge,
    gameState,
    isPreview,
  })

  logger.debug({ gameStateFromPlayerCookie: gameState })

  return c.html(
    `<!DOCTYPE html>` +
    (
      <Layout>
        <ChessArena gamePresenter={gamePresenter} boardId={boardId} />
      </Layout>
    ),
  )
})

dailyChallengeApp.get(DAILY_CHALLENGE_PATHS.HTMX_SELECT_PIECE, async (c) => {
  // TODO: validate the input data, using Zod
  const { boardId, square } = c.req.query()
  logger.debug({ boardId, square })

  const [challenge, isPreview] = await getCurrentDailyChallengeOrAdminPreview(c.req)
  const [gameState, created] = await getOrCreateDailyChallengeStateForPlayer({
    c,
    challenge,
  })
  if (created) {
    // we shouldn't have been creating a game at this point... Let's start a new game!
    return c.redirect(routes.MAIN_PAGE())
  }

  const gamePresenter = new DailyChallengeGamePresenter({
    challenge,
    gameState,
    isPreview,
    selectedPieceSquare: square as ChessSquare, //TODO: validate and remove cast
  })

  return c.html(
    <DailyChallengeMovingPartsFragment gamePresenter={gamePresenter} boardId={boardId} />,
  )
})

dailyChallengeApp.get(DAILY_CHALLENGE_PATHS.HTMX_MOVE_PIECE, async (c) => {
  // TODO: validate the input data, using Zod
  const { boardId, from, to } = c.req.query()
  logger.debug({ boardId, from, to })

  const [challenge, isPreview] = await getCurrentDailyChallengeOrAdminPreview(c.req)
  const [previousGameState, created] = await getOrCreateDailyChallengeStateForPlayer({
    c,
    challenge,
  })
  if (created) {
    // we shouldn't have been creating a game at this point... Let's start a new game!
    return c.redirect(routes.MAIN_PAGE())
  }

  const activePlayerSide = getActivePlayerSideFromFen(previousGameState.fen)
  const isMySide = activePlayerSide == challenge.mySide

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [newGameState, capturedPieceRole] = await moveDailyChallengePiece({
    gameState: previousGameState,
    from: from as ChessSquare, //TODO: validate and remove cast
    to: to as ChessSquare, //TODO: validate and remove cast
    isMySide,
  })

  const gamePresenter = new DailyChallengeGamePresenter({
    challenge,
    gameState: newGameState,
    isPreview,
  })

  return c.html(
    <DailyChallengeMovingPartsFragment gamePresenter={gamePresenter} boardId={boardId} />,
  )
})
