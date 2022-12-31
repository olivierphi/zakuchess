<script lang="ts">
	import { FILES, RANKS } from "$lib/domain/consts.js";
	import { squareToTailwindClasses } from "$lib/html-helpers.js";
	import type { Square } from "chess.js";

	const SQUARE_COLORS = ["bg-chess-square-dark-color", "bg-chess-square-light-color"];

	function squareClasses(file: string, rank: number, squareCounter: number): string[] {
		return [
			"absolute",
			"aspect-square",
			"w-1/8",
			SQUARE_COLORS[squareCounter % 2],
			...squareToTailwindClasses(`${file}${rank}` as Square)
		];
	}
</script>

<div id="chess-board-container" class="relative aspect-square border border-debug border-solid">
	{#each FILES as file, fileIndex}
		{#each RANKS as rank, rankIndex}
			<div class={squareClasses(file, rank, fileIndex + rankIndex).join(" ")}>
				<span class="text-chess-square-square-info">
					{rank === 1 ? file : ""}
					{file === "a" ? rank : ""}
				</span>
			</div>
		{/each}
	{/each}
</div>
