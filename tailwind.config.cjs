const chessBoardSpacing = Object.fromEntries([1,2,3,4,5,6,7].map(i => [`${i}/8`, `${i * 12.5}%`]))

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  safelist: chessRelatedClassesSafeList(),
  theme: {
    colors: {
      "debug1": "red",
      "debug2": "lime",
      "chess-square-light-color": "#e4b55d",
      "chess-square-dark-color": "#a57713",
      "chess-square-square-info": "#58400b",
    },
    fontFamily: {
      sans: ['OpenSans', 'sans-serif'],
      pixel: ['PixelFont', 'serif'],
    },
    extend: {
      width: {
        '1/8': '12.5%',
      },
      height: {
        '1/8': '12.5%',
      },
      inset: {
        ...chessBoardSpacing,
      },
      backgroundImage: {
        'wesnoth-loyalists-pawn': "url('/chess/units/default/fencer.png')",
        'wesnoth-loyalists-knight': "url('/chess/units/default/horseman.png')",
      },
      transitionProperty: {
        "coordinates": "top, left",
      }
    },
  },
  plugins: [],
}

function chessRelatedClassesSafeList() {
  	const COLUMNS_CLASSES = ["top-0", "top-1/8", "top-2/8", "top-3/8", "top-4/8", "top-5/8", "top-6/8", "top-7/8"];
	const RANK_CLASSES = ["left-0", "left-1/8", "left-2/8", "left-3/8", "left-4/8", "left-5/8", "left-6/8", "left-7/8"];
	const SQUARE_COLORS = ["bg-chess-square-dark-color", "bg-chess-square-light-color"];
  
  const PIECES_BACKGROUND_IMAGES = ["pawn", "knight"].map(pieceName => `bg-wesnoth-loyalists-${pieceName}`);
  
  return [...COLUMNS_CLASSES, ...RANK_CLASSES, ...SQUARE_COLORS, ...PIECES_BACKGROUND_IMAGES];
}
