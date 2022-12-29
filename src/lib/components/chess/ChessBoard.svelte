<script>
	import { FILES, RANKS } from "$lib/domain/consts.ts";
	import { squareToTailwindClasses } from "$lib/html-helpers.ts";
	const SQUARE_COLORS = ["bg-chess-square-dark-color", "bg-chess-square-light-color"];
</script>

<div class="relative aspect-square border border-debug border-solid">
	{#each FILES as file, fileIndex}
		{#each RANKS as rank, rankIndex}
			{@const classes = [
				"absolute",
				"aspect-square",
				"w-1/8",
				SQUARE_COLORS[(fileIndex + rankIndex) % 2],
				...squareToTailwindClasses(`${file}${rank}`)
			]}
			<div class={classes.join(" ")}>
				<span class="text-chess-square-square-info">
					{rank === 1 ? file : ""}
					{file === "a" ? rank : ""}
				</span>
			</div>
		{/each}
	{/each}
</div>
