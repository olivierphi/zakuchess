// import type { ChessGamePresenter } from "../business-logic/view-domain.js"
import type { FEN } from "~/business-logic/chess/chess.domain.ts"

import { ChessBoard } from "./ChessBoard.tsx"
// import { ChessPieceAvailableTargets } from "./ChessPieceAvailableTargets.js"
import { ChessPieces } from "./ChessPieces.tsx"

export type ChessArenaProps = {
    boardId: string
    fen: FEN | "start"
    //   gamePresenter: ChessGamePresenter
}

export function ChessArena({ boardId, fen }: ChessArenaProps) {
    const containersBasesClasses = "absolute inset-0 pointer-events-none"
    return (
        <div className="aspect-square relative" id={`chess-board-components-${boardId}`}>
            <div
                className="absolute inset-0 pointer-events-none z-0"
                id={`chess-board-container-${boardId}`}
            >
                <div
                    className={`${containersBasesClasses} z-0`}
                    id={`chess-board-container-${boardId}`}
                >
                    <ChessBoard boardId={boardId} />
                </div>
                <div
                    className={`${containersBasesClasses} z-20`}
                    id={`chess-pieces-container-${boardId}`}
                >
                    <ChessPieces fen={fen} boardId={boardId} />
                </div>
            </div>
        </div>
    )
}

// <div
//    className={`${containersBasesClasses} z-30`}
//    id={`chess-available-targets-container-${boardId}`}
//  >
//    <ChessPieceAvailableTargets gamePresenter={gamePresenter} boardId={boardId} />
//  </div>
