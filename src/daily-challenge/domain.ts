import type { FEN, PieceStateBySquare } from "../business-logic/chess-domain.js"

export type GameID = string

export type PlayerSessionContent = {
  // That is the content of the session cookie for the player.
  // Since it's just a Python dict, Django knows how to serialize it.
  games: Record<GameID, PlayerGameState>
}

export type PlayerGameState = {
  // That is the state of a daily challenge, stored in a cookie for the player.
  // Since it's just a Python dict, Django knows how to serialize it.
  attemptsCounter: number
  turnsCounter: number
  currentAttemptTurnsCounter: number
  fen: FEN
  pieceStateBySquare: PieceStateBySquare
  // Each move is 4 more chars added there (UCI notation, captures not recorded atm).
  // These are the moves *of the current attempt* only.
  moves: string
}

export type ChallengeTurnsState = {
  // the number of attempts the player has made for today's challenge:
  attemptsCounter: number
  // The number of turns in the current attempt:
  currentAttemptTurns: number
  turnsTotal: number
  turnsLeft: number
  percentageLeft: number
  timeIsUp: boolean // `True` when there are no more turns left for today's challenge.
}
