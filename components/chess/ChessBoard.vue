<script setup lang="ts">
import Square from "~/components/chess/Square.vue"
import { SQUARES } from "~/shared/business-logic/chess/chess-domain"

type Props = {
    boardId: string
}

defineProps<Props>()
</script>

<template>
    <div
        class="relative aspect-square pointer-events-none"
        :id="`chess-board-${boardId}`"
    >
        <Square v-for="square in SQUARES" :key="square" :square="square" />
    </div>
</template>
