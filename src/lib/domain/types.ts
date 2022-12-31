import type { Square as ChessSquare, PieceSymbol as ChessPieceSymbol } from "chess.js";

export type File = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h";
export type Rank = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8";

export type Square = ChessSquare;
export type PieceSymbol = ChessPieceSymbol;
export type TeamMemberRole = // 8 pawns:

		| "p1"
		| "p2"
		| "p3"
		| "p4"
		| "p5"
		| "p6"
		| "p7"
		| "p8"
		// 8 pieces:
		// N.B. Bishops are "b(lack)" or "w(hite)" rather than 1 or 2
		| "r1"
		| "n1"
		| "bb"
		| "q"
		| "k"
		| "bw"
		| "n2"
		| "r2";

export type PlayerSide = "w" | "b";

export type BoardPieces = Partial<Record<Square, Piece>>;

export type Piece = {
	role: TeamMemberRole;
	faction: string;
	square: Square; //TODO: get rid of this field
	piece: PieceSymbol;
	side: PlayerSide;
};
