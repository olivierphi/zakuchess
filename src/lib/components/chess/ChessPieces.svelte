<script lang="ts">
	import type { Square } from "chess.js";
	import { squareToTailwindClasses } from "$lib/html-helpers.ts";
	import { FILES } from "$lib/domain/consts";

	type Piece = {
		id: string;
		faction: string;
		square: Square;
		piece: string;
		side: "w" | "b";
	};

	let pieces: Piece[] = [
		...FILES.map((file) => ({
			id: `${file}2`,
			faction: "loyalists",
			square: `${file}2` as Square,
			piece: "pawn",
			side: "w"
		})),
		...FILES.map((file) => ({
			id: `${file}2`,
			faction: "loyalists",
			square: `${file}7` as Square,
			piece: "pawn",
			side: "b"
		})),
		{ id: "b1", faction: "loyalists", square: "b1", piece: "knight", side: "w" },
		{ id: "b1", faction: "loyalists", square: "g1", piece: "knight", side: "w" },
		{ id: "b1", faction: "loyalists", square: "b8", piece: "knight", side: "b" },
		{ id: "b1", faction: "loyalists", square: "g8", piece: "knight", side: "b" }
	];

	const pieceUnitClasses = (p: Piece): string[] => {
		const classes = [`bg-wesnoth-loyalists-${p.piece}`];
		if (p.side === "b") {
			classes.push("-scale-x-100");
		}
		return classes;
	};

	setTimeout(() => {
		pieces[4].square = "e4";
		pieces = pieces;
	}, 1000);
</script>

<div class="relative aspect-square border border-debug border-solid">
	{#each pieces as piece (piece.id)}
		{@const classes = [
			"absolute",
			"aspect-square",
			"w-1/8",
			...squareToTailwindClasses(piece.square),
			...pieceUnitClasses(piece),
			"transition-coordinates",
			"duration-300",
			"ease-in",
			"bg-no-repeat",
			"bg-cover"
		]}
		<div class={classes.join(" ")} />
	{/each}
</div>
