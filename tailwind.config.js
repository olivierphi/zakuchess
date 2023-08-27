const CHESS_BOARD_SPACING = Object.fromEntries([1, 2, 3, 4, 5, 6, 7].map((i) => [`${i}/8`, `${i * 12.5}%`]))
const PIECE_NAMES = ["pawn", "knight", "bishop", "rook", "queen", "king"]
const PLAYER_SIDES = ["w", "b"]
const FACTIONS = ["humans", "undeads"]

const ACTIVE_PLAYER_SELECTION_COLOR = "#ffff00"
const OPPONENT_PLAYER_SELECTION_COLOR = "#B0B000"
const POTENTIAL_CAPTURE_COLOR = "#c00000"
const PIECES_DROP_SHADOW_OFFSET = "1px"

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/apps/*/components/**/*.py"],
    safelist: chessRelatedClassesSafeList(),
    theme: {
        fontFamily: {
            sans: ["OpenSans", "sans-serif"],
            pixel: ["PixelFont", "monospace"],
            mono: ["monospace"],
        },
        extend: {
            colors: {
                "debug1": "red",
                "debug2": "lime",
                "chess-square-light": "#e4b55d", // "#fed7aa", // "#e4b55d", // "#fed7aa", // Tailwind's "Orange 200"
                "chess-square-dark": "#a57713", // "#881337", // Amber 700 // "#a57713", // "#9f1239", // Tailwind's "Rose 800"
                "chess-square-square-info": "#58400b",
                "active-chess-available-target-marker": ACTIVE_PLAYER_SELECTION_COLOR,
                "opponent-chess-available-target-marker": OPPONENT_PLAYER_SELECTION_COLOR,
            },
            width: {
                "1/8": "12.5%",
            },
            height: {
                "1/8": "12.5%",
            },
            spacing: {
                "0/1": "0",
                "1/1": "100%",
                "2/1": "200%",
                "3/1": "300%",
                "4/1": "400%",
                "5/1": "500%",
                "6/1": "600%",
                "7/1": "700%",
            },
            inset: {
                ...CHESS_BOARD_SPACING,
                "1/12": "8.333333%",
                "2/12": "16.666667%",
            },
            borderRadius: {
                "1/2": "50%",
            },
            backgroundImage: {
                ...chessSymbolsBackgroundImages(),
                ...chessCharactersBackgroundImages(),
            },
            transitionProperty: {
                coordinates: "transform, top, left",
                size: "width, height",
            },
            dropShadow: {
                "active-selected-piece": [
                    `${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${ACTIVE_PLAYER_SELECTION_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${ACTIVE_PLAYER_SELECTION_COLOR}`,
                    `${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${ACTIVE_PLAYER_SELECTION_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${ACTIVE_PLAYER_SELECTION_COLOR}`,
                ],
                "opponent-selected-piece": [
                    `${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${OPPONENT_PLAYER_SELECTION_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${OPPONENT_PLAYER_SELECTION_COLOR}`,
                    `${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${OPPONENT_PLAYER_SELECTION_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${OPPONENT_PLAYER_SELECTION_COLOR}`,
                ],
                "potential-capture": [
                    `${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${POTENTIAL_CAPTURE_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} ${PIECES_DROP_SHADOW_OFFSET} 0 ${POTENTIAL_CAPTURE_COLOR}`,
                    `${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${POTENTIAL_CAPTURE_COLOR}`,
                    `-${PIECES_DROP_SHADOW_OFFSET} -${PIECES_DROP_SHADOW_OFFSET} 0 ${POTENTIAL_CAPTURE_COLOR}`,
                ],
            },
        },
    },
    plugins: [],
}

function chessCharactersBackgroundImages() {
    return Object.fromEntries(
        FACTIONS.map((faction) =>
            PIECE_NAMES.map((pieceName) => [
                `${faction}-${pieceName}`,
                `url('/static/chess/units/${faction}/${pieceName}.png')`,
            ]),
        ).flat(),
    )
}

function chessSymbolsBackgroundImages() {
    return Object.fromEntries(
        PLAYER_SIDES.map((playerSide) =>
            PIECE_NAMES.map((pieceName) => [
                `${playerSide}-${pieceName}`,
                `url('/static/chess/symbols/${playerSide}-${pieceName}.svg')`,
            ]),
        ).flat(),
    )
}

function chessRelatedClassesSafeList() {
    const COLUMNS_CLASSES = ["top-0", "top-1/8", "top-2/8", "top-3/8", "top-4/8", "top-5/8", "top-6/8", "top-7/8"]
    const RANK_CLASSES = ["left-0", "left-1/8", "left-2/8", "left-3/8", "left-4/8", "left-5/8", "left-6/8", "left-7/8"]
    const SQUARE_COLORS = ["bg-chess-square-dark-color", "bg-chess-square-light-color"]

    return [...COLUMNS_CLASSES, ...RANK_CLASSES, ...SQUARE_COLORS]
}
