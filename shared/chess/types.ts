export type File = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h";
export type Rank = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8";

export type Square =
  | "a1"
  | "b1"
  | "c1"
  | "d1"
  | "e1"
  | "f1"
  | "g1"
  | "h1"
  | "a2"
  | "b2"
  | "c2"
  | "d2"
  | "e2"
  | "f2"
  | "g2"
  | "h2"
  | "a3"
  | "b3"
  | "c3"
  | "d3"
  | "e3"
  | "f3"
  | "g3"
  | "h3"
  | "a4"
  | "b4"
  | "c4"
  | "d4"
  | "e4"
  | "f4"
  | "g4"
  | "h4"
  | "a5"
  | "b5"
  | "c5"
  | "d5"
  | "e5"
  | "f5"
  | "g5"
  | "h5"
  | "a6"
  | "b6"
  | "c6"
  | "d6"
  | "e6"
  | "f6"
  | "g6"
  | "h6"
  | "a7"
  | "b7"
  | "c7"
  | "d7"
  | "e7"
  | "f7"
  | "g7"
  | "h7"
  | "a8"
  | "b8"
  | "c8"
  | "d8"
  | "e8"
  | "f8"
  | "g8"
  | "h8";
export type PieceType = "p" | "n" | "b" | "r" | "q" | "k";
export type PieceName =
  | "pawn"
  | "knight"
  | "bishop"
  | "rook"
  | "queen"
  | "king";
export type PlayerSide = "w" | "b";
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
    | "r1"
    | "n1"
    | "b1"
    | "q"
    | "k"
    | "b2"
    | "n2"
    | "r2";
export type PieceRole = // Same than TeamMemberRole, but applied to the board:
  // --> following chess conventions, "w player"'s pieces are uppercase while "b player"'s pieces are lowercase.
  // ----- "w" player side:
  | "P1"
  | "P2"
  | "P3"
  | "P4"
  | "P5"
  | "P6"
  | "P7"
  | "P8"
  | "R1"
  | "N1"
  | "B1"
  | "Q"
  | "K"
  | "B2"
  | "N2"
  | "R2"
  // Promoted pawns have a 3 letters role, where the last one is the promoted piece:
  // Let's consider "Queen" promotions only for now:
  | "P1Q"
  | "P2Q"
  | "P3Q"
  | "P4Q"
  | "P5Q"
  | "P6Q"
  | "P7Q"
  | "P8Q"
  // ----- "b" player side:
  | "p1"
  | "p2"
  | "p3"
  | "p4"
  | "p5"
  | "p6"
  | "p7"
  | "p8"
  | "r1"
  | "n1"
  | "b1"
  | "q"
  | "k"
  | "b2"
  | "n2"
  | "r2"
  // And same for "b" side promotions:
  | "p1q"
  | "p2q"
  | "p3q"
  | "p4q"
  | "p5q"
  | "p6q"
  | "p7q"
  | "p8q";
export type BoardOrientation = "1->8" | "8->1";
export type GamePhase =
  | "waiting_for_player_selection"
  | "player_move"
  | "bot_move"
  | "game_over";
export type UserPrefsGameSpeed = "NORMAL" | "FAST";
export type UserPrefsBoardTexture = "ABSTRACT" | "PLAIN";

export type Faction = "humans" | "undead";

export interface GameFactions {
  w: Faction;
  b: Faction;
}

export interface SelectedPiece {
  square: Square;
  player_side: PlayerSide;
  available_targets: Square[];
  is_potential_capture: (square: Square) => boolean;
}

export interface ChessArenaCompanionBars {
  top?: React.ReactNode;
  bottom?: React.ReactNode;
}
