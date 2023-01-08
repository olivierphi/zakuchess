import { FILES, RANKS } from "$lib/domain/chess/consts"
import type { Square } from "$lib/domain/chess/types"
import { squareToTailwindClasses } from "$lib/helpers/tailwind-helpers"

const SQUARE_COLOR_TAILWIND_CLASSES = ["bg-chess-square-dark-color", "bg-chess-square-light-color"]

export function ChessBoardBackground() {
	return (
		<div data-unit-type="chess-background" className="relative aspect-square pointer-events-none">
			{FILES.map((file, i): JSX.Element[] => {
				return RANKS.map((rank, j): JSX.Element => {
					const square = `${file}${rank}` as Square
					const squareIndex = i + j
					const classes = [
						"absolute",
						"aspect-square",
						"w-1/8",
						SQUARE_COLOR_TAILWIND_CLASSES[squareIndex % 2],
						...squareToTailwindClasses(square),
					]
					return (
						<div className={classes.join(" ")} key={square}>
							<span className="text-chess-square-square-info">
								{rank === "1" ? file : ""}
								{file === "a" ? rank : ""}
							</span>
						</div>
					)
				})
			}).flat()}
		</div>
	)
}
