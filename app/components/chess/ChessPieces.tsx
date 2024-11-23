import type { FEN } from "~/business-logic/chess/chess.domain"

type ChessPiecesProps = {
    fen: FEN | "start"
    boardId: string
}
export function ChessPieces({ fen, boardId }: ChessPiecesProps) {
    return (
        <div className="relative aspect-square pointer-events-none">
            {/* {SQUARES.map((square) => {
                return <ChessBoardSquare key={square} square={square} />;
            })} */}
        </div>
    )
}
