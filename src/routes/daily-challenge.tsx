import { Hono } from "hono"
import { ChessSquare } from "business-logic/chess-domain.js"
import { ChessArena } from "components/chess/ChessArena.js"
import { Layout } from "components/layout/Layout.js"
import { DAILY_CHALLENGE_PATHS, routes } from "daily-challenge/urls.js"
import { DailyChallengeMovingPartsFragment } from "../components/daily-challenge/DailyChallengeMovingPartsFragment.js"
import { DailyChallengeGamePresenter } from "../daily-challenge/presenters.js"
import { getCurrentDailyChallengeOrAdminPreview } from "../http/controller-helpers.js"
import { getOrCreateDailyChallengeStateForPlayer } from "../http/cookie-helpers.js"
import { logger } from "../logging.js"

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
