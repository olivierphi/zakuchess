import type { Context } from "hono"
import { getSignedCookie, setSignedCookie } from "hono/cookie"
import type { PlayerGameState, PlayerSessionContent } from "../daily-challenge/domain.js"
import type { DailyChallenge } from "../daily-challenge/models.js"
import { getSettings } from "../settings.js"

const PLAYER_CONTENT_SESSION_KEY = "pc"

type GetOrCreateDailyChallengeStateForPlayerProps = {
  c: Context
  challenge: DailyChallenge
}

export const getOrCreateDailyChallengeStateForPlayer = async ({
  c,
  challenge,
}: GetOrCreateDailyChallengeStateForPlayerProps): Promise<
  [gameState: PlayerGameState, created: boolean]
> => {
  /**
  Returns the game state for the given challenge, creating it if it doesn't exist yet.
  The second value is a boolean indicating if the game state was created or not.
  */
  const playerCookieContent = await getPlayerSessionContent(c)
  const challengeId = todayDailyChallengeId(c)
  let gameState: PlayerGameState | null =
    playerCookieContent["games"][challengeId] ?? null

  let created: boolean = false
  if (gameState === null) {
    gameState = await initialiseNewGameStateFromChallenge({ c, challenge })
    created = true
  }

  return [gameState, created]
}

const getPlayerSessionContent = async (c: Context): Promise<PlayerSessionContent> => {
  const playerCookieContentSerialised = await getSignedCookie(
    c,
    getSettings().COOKIES_SIGNING_SECRET,
    PLAYER_CONTENT_SESSION_KEY,
  )
  if (!playerCookieContentSerialised) {
    return { games: {} } //empty session
  }
  const cookieValue: PlayerSessionContent = JSON.parse(playerCookieContentSerialised)
  return cookieValue
}

const initialiseNewGameStateFromChallenge = async ({
  c,
  challenge,
}: {
  c: Context
  challenge: DailyChallenge
}): Promise<PlayerGameState> => {
  const gameState: PlayerGameState = {
    attemptsCounter: 0,
    turnsCounter: 0,
    currentAttemptTurnsCounter: 0,
    fen: challenge.fen,
    pieceStateBySquare: challenge.pieceStateBySquare,
    moves: "",
  }
  await saveDailyChallengeStateInSession({
    c,
    gameState,
  })
  return gameState
}

const saveDailyChallengeStateInSession = async ({
  c,
  gameState,
}: {
  c: Context
  gameState: PlayerGameState
}): Promise<void> => {
  // Erases other games data!
  const challengeId = todayDailyChallengeId(c)
  const cookieValue: PlayerSessionContent = { games: { [challengeId]: gameState } }
  const cookieValueSerialised = JSON.stringify(cookieValue)
  await setSignedCookie(
    c,
    PLAYER_CONTENT_SESSION_KEY,
    cookieValueSerialised,
    getSettings().COOKIES_SIGNING_SECRET,
  )
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const clearDailyChallengesStateInSession = async (c: Context): Promise<void> => {
  // Erases all games data!
  const cookieValue: PlayerSessionContent = { games: {} }
  const cookieValueSerialised = JSON.stringify(cookieValue)
  await setSignedCookie(
    c,
    PLAYER_CONTENT_SESSION_KEY,
    cookieValueSerialised,
    getSettings().COOKIES_SIGNING_SECRET,
  )
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const todayDailyChallengeId = (c: Context): string => {
  //if request.user.is_staff // TODO: implement this
  return new Date().toISOString().slice(0, 10)
}
