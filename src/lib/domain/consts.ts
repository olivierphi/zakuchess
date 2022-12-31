import type { File, Rank, PieceSymbol, Square, TeamMemberRole } from "$lib/domain/types.js";

export const FILES: Readonly<File[]> = ["a", "b", "c", "d", "e", "f", "g", "h"];
export const RANKS: Readonly<Rank[]> = ["1", "2", "3", "4", "5", "6", "7", "8"];

export const PIECE_ID_TO_NAME: Readonly<Record<PieceSymbol, string>> = {
	p: "pawn",
	n: "knight",
	b: "bishop",
	r: "rook",
	q: "queen",
	k: "king",
};

export const PIECES_ROLE_BY_STARTING_SQUARE: Readonly<Partial<Record<Square, TeamMemberRole>>> = {
	// Side "w":
	a1: "r1",
	b1: "n1",
	c1: "bb",
	d1: "q",
	e1: "k",
	f1: "bw",
	g1: "n2",
	h1: "r2",
	a2: "p1",
	b2: "p2",
	c2: "p3",
	d2: "p4",
	e2: "p5",
	f2: "p6",
	g2: "p7",
	h2: "p8",
	// Side "b":
	a8: "r1",
	b8: "n1",
	c8: "bw",
	d8: "q",
	e8: "k",
	f8: "bb",
	g8: "n2",
	h8: "r2",
	a7: "p1",
	b7: "p2",
	c7: "p3",
	d7: "p4",
	e7: "p5",
	f7: "p6",
	g7: "p7",
	h7: "p8",
};
