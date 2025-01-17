<script setup lang="ts">
import {
    type ChessFile,
    type ChessRank,
    type ChessSquare,
    FILE_NAMES,
    RANK_NAMES,
} from "~/shared/business-logic/chess/chess-domain"

import { squareToPieceTailwindClasses } from "./chess-components-helpers"

type Props = {
    square: ChessSquare
    forceSquareInfo?: boolean
}

const props = defineProps<Props>()

const _SQUARE_COLOR_TAILWIND_CLASSES = [
    "bg-chess-square-dark",
    "bg-chess-square-light",
] as const

const file = computed(() => props.square[0] as ChessFile)
const rank = computed(() => props.square[1] as ChessRank)

const squareIndex = computed(
    () => FILE_NAMES.indexOf(file.value) + RANK_NAMES.indexOf(rank.value),
)
const squareColorClass = computed(
    () => _SQUARE_COLOR_TAILWIND_CLASSES[squareIndex.value % 2],
)
const classes = computed(() => [
    "absolute",
    "aspect-square",
    "w-1/8",
    squareColorClass.value,
    ...squareToPieceTailwindClasses(props.square),
])

const displaySquareInfo = computed(() =>
    Boolean(props.forceSquareInfo || file.value == "a" || rank.value == "1"),
)
const squareName = computed(() =>
    props.forceSquareInfo
        ? `${file.value}${rank.value}`
        : [rank.value == "1" ? file.value : "", file.value == "a" ? rank.value : ""].join(
              "",
          ),
)
</script>

<template>
    <div :class="classes.join(' ')" :data-square="square">
        <span v-if="displaySquareInfo" class="text-chess-square-square-info">
            {{ squareName }}
        </span>
    </div>
</template>
