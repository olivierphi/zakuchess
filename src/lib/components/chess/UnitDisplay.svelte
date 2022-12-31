<script lang="ts">
	import { PIECE_ID_TO_NAME } from "$lib/domain/consts";
	import type { Piece } from "$lib/domain/types";

	export let piece: Piece;

	const specificUnitClasses = (piece: Piece): string[] => {
		const classes = [`bg-wesnoth-loyalists-${PIECE_ID_TO_NAME[piece.piece]}`];
		if (piece.side === "b") {
			classes.push("-scale-x-100");
		}
		return classes;
	};

	function unitClasses(piece: Piece): string[] {
		return ["relative", "w-full", "aspect-square", "bg-no-repeat", "bg-cover", "z-10", ...specificUnitClasses(piece)];
	}
</script>

<div class={unitClasses(piece).join(" ")} />
