<script lang="ts">
	import type { Square, Piece, PlayerSide, PieceSymbol } from "$lib/domain/types.js";
	import { FILES } from "$lib/domain/consts.js";
	import { squareToTailwindClasses } from "$lib/html-helpers.js";
	import UnitDisplay from "./UnitDisplay.svelte";

	let pieces: Piece[] = [
		...FILES.map((file) => ({
			id: `w-${file}2`,
			faction: "loyalists",
			square: `${file}2` as Square,
			piece: "p" as PieceSymbol,
			side: "w" as PlayerSide
		})),
		...FILES.map((file) => ({
			id: `b-${file}2`,
			faction: "loyalists",
			square: `${file}7` as Square,
			piece: "p" as PieceSymbol,
			side: "b" as PlayerSide
		})),
		{ id: "w-b1", faction: "loyalists", square: "b1", piece: "n", side: "w" },
		{ id: "w-g1", faction: "loyalists", square: "g1", piece: "n", side: "w" },
		{ id: "b-b8", faction: "loyalists", square: "b8", piece: "n", side: "b" },
		{ id: "b-g8", faction: "loyalists", square: "g8", piece: "n", side: "b" }
	];

	function pieceClasses(square: Square): string[] {
		return [
			"absolute",
			"aspect-square",
			"w-1/8",
			"cursor-pointer",
			"pointer-events-auto",
			...squareToTailwindClasses(square),
			// Transition-related classes:
			"transition-coordinates",
			"duration-200",
			"ease-in",
			"transform-gpu"
		];
	}

	setTimeout(() => {
		pieces[16].square = "c3";
		pieces = pieces;
	}, 1000);
	setTimeout(() => {
		pieces[17].square = "f3";
		pieces = pieces;
	}, 2000);
</script>

<div id="chess-pieces-container" class="relative aspect-square border border-debug border-solid">
	{#each pieces as piece (piece.id)}
		<div id={`piece-${piece.side}-${piece.id}`} class={pieceClasses(piece.square).join(" ")} data-unit-id={piece.id}>
			<UnitDisplay {piece} />
		</div>
	{/each}
</div>
