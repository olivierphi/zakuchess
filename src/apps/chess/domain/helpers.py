from functools import cache
from typing import TYPE_CHECKING, cast

import chess

from .consts import PIECE_INT_TO_PIECE_TYPE, PIECE_TYPE_TO_NAME, PIECE_TYPE_TO_UNICODE, SQUARES
from .types import PieceType

if TYPE_CHECKING:
    from .types import File, PieceRole, PieceSymbol, PlayerSide, Rank, Square, TeamMemberRole


@cache
def square_from_int(chess_lib_square: int) -> "Square":
    return cast("Square", chess.square_name(chess_lib_square))


@cache
def piece_from_int(chess_lib_piece: int) -> PieceType:
    # a bit hacky but that will do the job for now ^^
    return PIECE_INT_TO_PIECE_TYPE[chess_lib_piece]


@cache
def player_side_other(player_side: "PlayerSide") -> "PlayerSide":
    return "w" if player_side == "b" else "b"


@cache
def symbol_from_piece_role(piece_role: "PieceRole") -> "PieceSymbol":
    # If it's a promoted pawn (len == 3), we want the last character, which is the promoted piece.
    return cast("PieceSymbol", piece_role[0] if len(piece_role) == 2 else piece_role[-1])


@cache
def type_from_piece_role(piece_role: "PieceRole") -> "PieceType":
    return cast("PieceType", symbol_from_piece_role(piece_role).lower())


@cache
def type_from_piece_symbol(piece_symbol: "PieceSymbol") -> "PieceType":
    return cast("PieceType", piece_symbol.lower())


@cache
def player_side_from_piece_role(piece_role: "PieceRole") -> "PlayerSide":
    return "w" if symbol_from_piece_role(piece_role).isupper() else "b"


@cache
def team_member_role_from_piece_role(piece_role: "PieceRole") -> "TeamMemberRole":
    return cast("TeamMemberRole", piece_role[0:2].lower())


@cache
def piece_role_from_team_member_role_and_player_side(
    team_member_role: "TeamMemberRole", player_side: "PlayerSide"
) -> "PieceRole":
    return cast("PieceRole", team_member_role.upper() if player_side == "w" else team_member_role)


@cache
def file_and_rank_from_square(square: "Square") -> tuple["File", "Rank"]:
    return cast("File", square[0]), cast("Rank", square[1])


@cache
def piece_name_from_piece_type(piece_type: "PieceType") -> str:
    return PIECE_TYPE_TO_NAME[piece_type]


@cache
def piece_name_from_piece_role(piece_role: "PieceRole") -> str:
    return piece_name_from_piece_type(type_from_piece_role(piece_role))


@cache
def utf8_symbol_from_piece_type(piece_type: "PieceType") -> str:
    return PIECE_TYPE_TO_UNICODE[piece_type]


@cache
def utf8_symbol_from_piece_role(piece_role: "PieceRole") -> str:
    return utf8_symbol_from_piece_type(type_from_piece_role(piece_role))


def get_squares_with_pieces_that_can_move(board: chess.Board) -> frozenset["Square"]:
    return frozenset(cast("Square", chess.square_name(move.from_square)) for move in board.legal_moves)


def get_active_player_from_chess_board(board: chess.Board) -> "PlayerSide":
    return "w" if board.turn else "b"


@cache
def get_square_order(square: "Square") -> int:
    return SQUARES.index(square)
