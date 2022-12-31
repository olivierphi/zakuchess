import { Chess } from "chess.js";
import type { Color } from "chess.js";
import type { Square, BoardPieces, PieceSymbol } from "../types";
import { isNotNull } from "$lib/ts-type-predcates";
import { PIECES_ROLE_BY_STARTING_SQUARE } from "../consts";

const DEFAULT_STARTING_GAME = new Chess();
const DEFAULT_STARTING_BOARD: Readonly<
	{
		square: Square;
		type: PieceSymbol;
		color: Color;
	}[]
> = DEFAULT_STARTING_GAME.board()[0].filter(isNotNull);

export function getNewGameData(): BoardPieces {
	return Object.fromEntries(
		DEFAULT_STARTING_BOARD.map((startingSquareData) => {
			const { square, type, color } = startingSquareData;
			return [
				square,
				{
					role: PIECES_ROLE_BY_STARTING_SQUARE[square],
					faction: "wesnoth-loyalists",
					square: square,
					piece: type,
					side: color,
				},
			];
		}),
	);
}
