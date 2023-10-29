import { type FC, Fragment } from "hono/jsx"
import { ChessPieceAvailableTargets } from "apps/chess/components/ChessPieceAvailableTargets.js"
import { ChessPieces } from "apps/chess/components/ChessPieces.js"
import type { DailyChallengeGamePresenter } from "../business-logic/presenters.js"

export type DailyChallengeMovingPartsFragmentProps = {
  gamePresenter: DailyChallengeGamePresenter
  boardId: string
}
export const DailyChallengeMovingPartsFragment: FC<
  DailyChallengeMovingPartsFragmentProps
> = ({ gamePresenter, boardId }) => {
  return (
    <Fragment>
      <ChessPieces gamePresenter={gamePresenter} boardId={boardId} />
      <ChessPieceAvailableTargets
        gamePresenter={gamePresenter}
        boardId={boardId}
        data-hx-swap-oob="outerHTML"
      />
    </Fragment>
  )
}
