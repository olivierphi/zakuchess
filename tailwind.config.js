const CHESS_BOARD_SQUARES_TRANSLATION_SPACING = Object.fromEntries(
    [1, 2, 3, 4, 5, 6, 7, 8].map((i) => [`${i}/8`, `${i * 12.5}%`]),
)
const CHESS_BOARD_SQUARES_ABSOLUTE_POSITION_SPACING = Object.fromEntries(
    [1, 2, 3, 4, 5, 6, 7, 8].map((i) => [`${i}/8%`, `${i * 12.5 - 12.5 / 2}%`]),
)
const PIECE_NAMES = ["pawn", "knight", "bishop", "rook", "queen", "king"]
const PLAYER_SIDES = ["w", "b"]
const FACTIONS = ["humans", "undeads"]

const ACTIVE_PLAYER_SELECTION_COLOR = "#ffff00"
const OPPONENT_PLAYER_SELECTION_COLOR = "#ffd000"
const POTENTIAL_CAPTURE_COLOR = "#c00000"
const PIECE_SYMBOL_BORDER_OPACITY = Math.round(0.4 * 0xff).toString(16) // 40% of 255
const PIECE_SYMBOL_W = `#065f46${PIECE_SYMBOL_BORDER_OPACITY}` // emerald-800
const PIECE_SYMBOL_B = `#3730a3${PIECE_SYMBOL_BORDER_OPACITY}` // indigo-800
const PIECES_DROP_SHADOW_OFFSET = 1 // px
const SPEECH_BUBBLE_DROP_SHADOW_COLOR = "#fbbf24" // amber-400

// https://github.com/tailwindlabs/tailwindcss/blob/main/stubs/config.full.js

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/apps/*/components/**/*.py"],
    safelist: chessRelatedClassesSafeList(),
    theme: {
        fontFamily: {
            sans: ["Open Sans", "sans-serif"],
            pixel: ["PixelFont", "monospace"],
            mono: ["monospace"],
        },
        extend: {
            colors: {
                "debug1": "red",
                "debug2": "lime",
                "chess-square-light": "#e4b55d", // "#fed7aa", // "#e4b55d", // "#fed7aa",
                "chess-square-dark": "#a57713", // "#881337", // Amber 700 // "#a57713", // "#9f1239",
                "chess-square-square-info": "#58400b",
                "body-background": "#120222", // @link https://www.tints.dev/purple/A855F7
                "active-chess-available-target-marker": ACTIVE_PLAYER_SELECTION_COLOR,
                "opponent-chess-available-target-marker": OPPONENT_PLAYER_SELECTION_COLOR,
            },
            width: {
                "1/8": "12.5%",
            },
            height: {
                "1/8": "12.5%",
            },
            minWidth: {
                40: "10rem" /* 160px */,
            },
            minHeight: {
                40: "10rem" /* 160px */,
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
                "1/2": "50%",
            },
            inset: {
                ...CHESS_BOARD_SQUARES_TRANSLATION_SPACING,
                ...CHESS_BOARD_SQUARES_ABSOLUTE_POSITION_SPACING,
                "1/12": "8.333333%",
                "2/12": "16.666667%",
                "1/24": "4.166667%",
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
                // "piece-symbol-w": `0 0 0.1rem ${PIECE_SYMBOL_W}`,
                // "piece-symbol-b": `0 0 0.1rem ${PIECE_SYMBOL_B}`,
                "piece-symbol-w": borderFromDropShadow(1, PIECE_SYMBOL_W),
                "piece-symbol-b": borderFromDropShadow(1, PIECE_SYMBOL_B),
                "active-selected-piece": borderFromDropShadow(
                    PIECES_DROP_SHADOW_OFFSET,
                    ACTIVE_PLAYER_SELECTION_COLOR,
                ),
                "opponent-selected-piece": borderFromDropShadow(
                    PIECES_DROP_SHADOW_OFFSET,
                    OPPONENT_PLAYER_SELECTION_COLOR,
                ),
                "potential-capture": borderFromDropShadow(PIECES_DROP_SHADOW_OFFSET, POTENTIAL_CAPTURE_COLOR),
                "speech-bubble": `0 0 2px ${SPEECH_BUBBLE_DROP_SHADOW_COLOR}`,
            },
        },
    },
    plugins: [],
}

function borderFromDropShadow(offset, color, unit = "px") {
    let dropShadow = []
    for (const [x, y] of [
        [offset, offset],
        [-offset, offset],
        [offset, -offset],
        [-offset, -offset],
    ]) {
        dropShadow.push(`${x}${unit} ${y}${unit} 0 ${color}`)
    }
    return dropShadow
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
