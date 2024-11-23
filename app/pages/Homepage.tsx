import type { MetaFunction } from "react-router"

import { ChessArena } from "~/components/chess/ChessArena.tsx"

export default function Homepage() {
    return (
        <main>
            <h1 className="text-amber-200">Hi there</h1>
            <ChessArena fen="start" boardId="main" />
        </main>
    )
}

export const meta: MetaFunction = () => {
    return [
        { title: "ZakuChess ♞" },
        { name: "description", content: "ZakuChess" },
        { name: "keywords", content: "chess roleplay pixel-art" },
    ]
}
