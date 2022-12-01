export type { Square } from 'chess.js'

export type FEN = string // @link https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation

export type PlayerSide = "w" | "b" // Following chess conventions, our side will be "w(hite)" and "b(lack)".

export type GamePhase = "waiting_for_piece_selection" | "waiting_for_selected_piece_target"
