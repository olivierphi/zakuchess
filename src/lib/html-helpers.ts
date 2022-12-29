import type { Square } from "chess.js";
import type { File, Rank } from "$lib/html-helpers.ts";

const FILE_TO_TAILWIND_POSITIONING_CLASS: Record<File, string> = {
	a: "top-0/8",
	b: "top-1/8",
	c: "top-2/8",
	d: "top-3/8",
	e: "top-4/8",
	f: "top-5/8",
	g: "top-6/8",
	h: "top-7/8"
};
const RANK_TO_TAILWIND_POSITIONING_CLASS: Record<Rank, string> = {
	1: "left-0/8",
	2: "left-1/8",
	3: "left-2/8",
	4: "left-3/8",
	5: "left-4/8",
	6: "left-5/8",
	7: "left-6/8",
	8: "left-7/8"
};

export const squareToTailwindClasses = (square: Square): string[] => {
	const [file, rank] = square;
	return [FILE_TO_TAILWIND_POSITIONING_CLASS[file], RANK_TO_TAILWIND_POSITIONING_CLASS[rank]];
};
