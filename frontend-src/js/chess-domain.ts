export type { Square, PieceSymbol } from "chess.js"

export type FEN = string // @link https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation

export type PlayerSide = "w" | "b" // Following chess conventions, our side will be "w(hite)" and "b(lack)".

export type GamePhase = "waiting_for_piece_selection" | "waiting_for_selected_piece_target"

export type TeamMembersByRoleBySide = Record<PlayerSide, Record<TeamMembersRole, TeamMember>>

export type TeamMembersRole =
    // 8 pawns:
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
    | "r2"

export type TeamMember = {
    first_name: string
    last_name: string
    role: TeamMembersRole
}
