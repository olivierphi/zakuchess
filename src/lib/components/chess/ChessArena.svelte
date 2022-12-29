<script>
	import ChessBoard from "./ChessBoard.svelte";
	import ChessPieces from "./ChessPieces.svelte";
</script>

<div class="w-full md:max-w-xl mx-auto aspect-square relative border border-debug2 border-solid">
	<div class="absolute inset-0 z-0">
		<ChessBoard />
	</div>
	<div class="absolute inset-0 z-10">
		<ChessPieces />
	</div>
</div>
