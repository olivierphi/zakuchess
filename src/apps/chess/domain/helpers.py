from functools import cache
from typing import TYPE_CHECKING, cast

import chess

from .consts import PIECE_TYPE_TO_NAME, PIECE_TYPE_TO_UNICODE

if TYPE_CHECKING:
    from .types import File, PieceRole, PieceSymbol, PieceType, PlayerSide, Rank, Square, TeamMemberRole


@cache
def square_from_int(chess_lib_square: int) -> "Square":
    return cast("Square", chess.square_name(chess_lib_square))


@cache
def player_side_other(player_side: "PlayerSide") -> "PlayerSide":
    return "w" if player_side == "b" else "w"


@cache
def symbol_from_piece_role(piece_role: "PieceRole") -> "PieceSymbol":
    return cast("PieceSymbol", piece_role[0])


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
    return cast("TeamMemberRole", piece_role.lower())


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


def get_squares_with_pieces_that_can_move(board: chess.Board) -> set["Square"]:
    return set(cast("Square", chess.square_name(move.from_square)) for move in board.legal_moves)
