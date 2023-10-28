import { FC, Fragment } from "hono/jsx"
import { ChessPieceAvailableTargets } from "components/chess/ChessPieceAvailableTargets.js"
import type { DailyChallengeGamePresenter } from "../../daily-challenge/presenters.js"
import { ChessPieces } from "../chess/ChessPieces.js"

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
