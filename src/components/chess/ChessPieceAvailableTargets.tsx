import { FC } from "hono/jsx"
import type { ChessSquare, PlayerSide } from "business-logic/chess-domain.js"
import type { ChessGamePresenter } from "business-logic/view-domain.js"
import { squareToPieceTailwindClasses } from "components/chess-components-helpers.js"

export type ChessPieceAvailableTargetsProps = {
  gamePresenter: ChessGamePresenter
  boardId: string
} & Record<string, unknown> // additional props for htmx

export const ChessPieceAvailableTargets: FC<ChessPieceAvailableTargetsProps> = ({
  gamePresenter,
  boardId,
  ...additionalProps
}) => {
  const children = []
  if (gamePresenter.selectedPiece && !gamePresenter.isGameOver) {
    const side = gamePresenter.selectedPiece.playerSide
    for (const square of gamePresenter.selectedPiece.availableTargets) {
      children.push(
        <ChessPieceAvailableTarget
          gamePresenter={gamePresenter}
          square={square}
          side={side}
          boardId={boardId}
        />,
      )
    }
  }

  return (
    <div
      class="relative aspect-square pointer-events-none"
      id={`chess-board-available-targets-${boardId}`}
      {...additionalProps}
    >
      {children}
    </div>
  )
}

type ChessPieceAvailableTargetProps = {
  gamePresenter: ChessGamePresenter
  square: ChessSquare
  side: PlayerSide
  boardId: string
}

const ChessPieceAvailableTarget: FC<ChessPieceAvailableTargetProps> = ({
  gamePresenter,
  square,
  side,
  boardId,
}) => {
  const canMove = !gamePresenter.isGameOver && gamePresenter.activePlayerSide === side
  const bgClass = canMove
    ? "bg-active-chess-available-target-marker"
    : "bg-opponent-chess-available-target-marker"
  const hoverClass = canMove ? "hover:w-1/3 hover:h-1/3" : ""

  const targetMarker = (
    <div class={`w-1/5 h-1/5 rounded-full transition-size ${bgClass} ${hoverClass}`} />
  )
  const targetMarkerContainer = (
    <div class="w-full aspect-square flex items-center justify-center">
      {targetMarker}
    </div>
  )

  const targetClasses = [
    "absolute",
    "aspect-square",
    "w-1/8",
    ...squareToPieceTailwindClasses(square),
    ...(canMove ? ["cursor-pointer", "pointer-events-auto"] : ["pointer-events-none"]),
  ]

  const htmxAttributes = {}
  if (canMove) {
    Object.assign(htmxAttributes, {
      "data-hx-post": gamePresenter.urls.htmxGameMovePiece({ square, boardId }),
      "data-hx-target": `#chess-board-pieces-${boardId}`,
      "data-hx-swap": "outerHTML",
    })
  }

  return (
    <div class={targetClasses.join(" ")} {...htmxAttributes} data-square={square}>
      {targetMarkerContainer}
    </div>
  )
}
