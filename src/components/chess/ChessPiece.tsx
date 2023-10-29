import { FC } from "hono/jsx"
import { playerSideFromPieceState } from "business-logic/chess-helpers.js"
import type { ChessSquare, PieceState } from "../../business-logic/chess-domain.js"
import type { ChessGamePresenter } from "../../business-logic/view-domain.js"
import { squareToPieceTailwindClasses } from "../chess-components-helpers.js"
import { ChessCharacterDisplay } from "./ChessCharacterDisplay.js"
import { ChessGroundMarker } from "./ChessGroundMarker.js"
import { ChessUnitSymbolDisplay } from "./ChessUnitSymbolDisplay.js"

export type ChessPieceProps = {
  boardId: string
  gamePresenter: ChessGamePresenter
  square: ChessSquare
  state: PieceState
}

export const ChessPiece: FC<ChessPieceProps> = ({
  boardId,
  gamePresenter,
  square,
  state,
}) => {
  const side = playerSideFromPieceState(state)
  const pieceCanMove =
    gamePresenter.isPlayerTurn &&
    gamePresenter.squaresWithPiecesThatCanMove.includes(square)
  const isSelectedPiece = gamePresenter.selectedPiece?.square === square
  const isGameOver = false //TODO

  const classes = [
    "absolute",
    "aspect-square",
    "w-1/8",
    ...squareToPieceTailwindClasses(square),
    isGameOver ? "cursor-default" : "cursor-pointer",
    isGameOver ? "pointer-events-none" : "pointer-events-auto",
    // Transition-related classes:
    "transition-coordinates",
    "duration-300",
    "ease-in",
    "transform-gpu",
  ]

  const htmxAttributes = {}
  if (!isGameOver) {
    Object.assign(htmxAttributes, {
      "data-hx-trigger": "click",
      "data-hx-get": isSelectedPiece
        ? // Re-selecting an already selected piece de-selects it:
          gamePresenter.urls.htmxGameNoSelection({ boardId })
        : gamePresenter.urls.htmxGameSelectPiece({ square, boardId }),
      "data-hx-target": `#chess-board-pieces-${boardId}`,
    })
  }

  return (
    <div
      class={classes.join(" ")}
      data-square={square}
      data-piece-state={state}
      {...htmxAttributes}
    >
      <ChessGroundMarker side={side} pieceCanMove={pieceCanMove} />
      <ChessCharacterDisplay
        state={state}
        gamePresenter={gamePresenter}
        square={square}
      />
      <ChessUnitSymbolDisplay state={state} />
    </div>
  )
}
