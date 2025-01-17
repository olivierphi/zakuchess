<script setup lang="ts">
type Props = {
    boardId: string
}

defineProps<Props>()
</script>

<template>
    <section
        class="w-full mx-auto bg-slate-900 md:max-w-3xl xl:max-w-7xl xl:flex xl:border xl:rounded-md xl:border-neutral-800"
    >
        <div class="xl:w-2/3 bg-slate-800" :id="`chess-board-components-${boardId}`">
            <div class="aspect-square relative mx-auto max-w-[calc(100dvh-80px)]">
                <div
                    class="absolute inset-0 pointer-events-none z-0"
                    :id="`chess-board-container-${boardId}`"
                >
                    <ChessBoard :boardId="boardId" />
                </div>
                <div
                    class="absolute inset-0 pointer-events-none z-20"
                    :id="`chess-pieces-container-${boardId}`"
                >
                    <ChessPieces :boardId="boardId" />
                </div>
            </div>
        </div>
    </section>
</template>
