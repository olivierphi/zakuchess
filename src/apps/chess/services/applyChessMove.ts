import { Chess, type Move } from "chess.js"
import type {
  ChessMoveChanges,
  ChessMoveResult,
  ChessSquare,
  FEN,
  PlayerSide,
  Promotion,
} from "../business-logic/chess-domain.js"
import { GameEndReason, GameOverDescription } from "../business-logic/chess-domain.js"

type ApplyChessMoveParams = {
  fen: FEN
  from: ChessSquare
  to: ChessSquare
}

export const applyChessMove = ({
  fen,
  from,
  to,
}: ApplyChessMoveParams): ChessMoveResult => {
  const changes: ChessMoveChanges = {}
  const chessBoard = new Chess(fen)

  const currentPiece = chessBoard.get(from)
  if (!currentPiece) {
    throw new Error(`No pieces on selected square '${from}'`)
  }
  const isPromotion = currentPiece.type === "p" && (to[1] === "1" || to[1] === "8")
  // TODO: allow the user to choose the promotion piece?
  const promotionPiece = isPromotion ? "q" : undefined
  let chessMove: Move
  try {
    chessMove = chessBoard.move({ from, to, promotion: promotionPiece }, { strict: true })
  } catch (err) {
    throw new Error(`Invalid move ${from}->${to} for FEN '${fen}': ${err}`)
  }
  const isCapture = chessMove.captured !== undefined
  const isCastling =
    !isCapture && (chessMove.flags.includes("k") || chessMove.flags.includes("q"))
  const promotion = (chessMove.promotion as Promotion | undefined) ?? null

  // Record that piece's move:
  changes[from] = to
  // Record the capture, if any:
  if (isCapture) {
    changes[to] = null
  }
  // Specific cases:
  if (isCastling) {
    // Castling: move the rook as well
    const rookFrom = (
      chessMove.flags.includes("q") ? "a" + from[1] : "h" + from[1]
    ) as ChessSquare
    const rookTo = (
      chessMove.flags.includes("q") ? "d" + from[1] : "f" + from[1]
    ) as ChessSquare
    changes[rookFrom] = rookTo
  }

  // Check the game's outcome:
  let gameOver: GameOverDescription | null = null
  if (chessBoard.isGameOver()) {
    const winner: PlayerSide | null = chessBoard.isCheckmate()
      ? chessBoard.turn() === "w"
        ? "b"
        : "w"
      : null
    const gameEndReason = getGameEndReason(chessBoard)
    gameOver = { winner, reason: gameEndReason }
  }

  const newFen: FEN = chessBoard.fen()

  return {
    fen: newFen,
    changes,
    isCapture,
    isCastling,
    promotion,
    gameOver,
  }
}

const getGameEndReason = (chessBoard: Chess): GameEndReason => {
  // N.B. Contrary to python-chess, Chess.js doesn't manage the following cases:
  // - fivefold_repetition
  // - seventyfive_moves

  switch (true) {
    case chessBoard.isStalemate():
      return "stalemate"
    case chessBoard.isInsufficientMaterial():
      return "insufficient_material"
    case chessBoard.isThreefoldRepetition():
      return "threefold_repetition"
  }

  // If it's none of the other reasons, it's a draw by the 50 moves rule:
  return "fifty_moves"
}
