from functools import cache, lru_cache
from typing import TYPE_CHECKING, cast

import chess

from .consts import (
    FILES,
    PIECE_INT_TO_PIECE_TYPE,
    PIECE_TYPE_TO_NAME,
    PIECE_TYPE_TO_UNICODE,
    RANKS,
    SQUARES,
)

if TYPE_CHECKING:
    from .types import (
        FEN,
        File,
        PieceName,
        PieceRole,
        PieceSymbol,
        PieceType,
        PlayerSide,
        Rank,
        Square,
        TeamMemberRole,
    )


@cache
def chess_lib_square_to_square(chess_lib_square: int) -> "Square":
    return cast("Square", chess.square_name(chess_lib_square))


@cache
def chess_lib_piece_to_piece_type(chess_lib_piece: int) -> "PieceType":
    # a bit hacky but that will do the job for now ^^
    return PIECE_INT_TO_PIECE_TYPE[chess_lib_piece]


@cache
def player_side_other(player_side: "PlayerSide") -> "PlayerSide":
    return "w" if player_side == "b" else "b"


@cache
def symbol_from_piece_role(piece_role: "PieceRole") -> "PieceSymbol":
    # If it's a promoted pawn (len == 3), we want the last character
    # (which is the promoted piece in such a case)
    return cast(
        "PieceSymbol", piece_role[0] if len(piece_role) == 2 else piece_role[-1]
    )


@cache
def type_from_piece_role(piece_role: "PieceRole") -> "PieceType":
    return cast("PieceType", symbol_from_piece_role(piece_role).lower())


@cache
def type_from_piece_symbol(piece_symbol: "PieceSymbol") -> "PieceType":
    return cast("PieceType", piece_symbol.lower())


@cache
def player_side_from_piece_symbol(piece_role: "PieceSymbol") -> "PlayerSide":
    return "w" if piece_role.isupper() else "b"


@cache
def player_side_from_piece_role(piece_role: "PieceRole") -> "PlayerSide":
    return player_side_from_piece_symbol(piece_role)


@cache
def team_member_role_from_piece_role(piece_role: "PieceRole") -> "TeamMemberRole":
    return cast("TeamMemberRole", piece_role[0:2].lower())


@cache
def piece_role_from_team_member_role_and_player_side(
    team_member_role: "TeamMemberRole", player_side: "PlayerSide"
) -> "PieceRole":
    return cast(
        "PieceRole",
        team_member_role.upper() if player_side == "w" else team_member_role,
    )


@cache
def file_and_rank_from_square(square: "Square") -> tuple["File", "Rank"]:
    file, rank = square[0], square[1]
    # As the result is cached, we can allow ourselves some sanity checks
    # when Python's "optimization mode" is requested:
    assert file in FILES and rank in RANKS, f"square '{square}' is not valid"
    return cast("File", file), cast("Rank", rank)


@cache
def square_from_file_and_rank(file: "File", rank: "Rank") -> "Square":
    """Inverse of the function above"""
    # ditto
    assert file in FILES, f"file '{file}' is not valid"
    assert rank in RANKS, f"rank '{rank}' is not valid"
    return cast("Square", f"{file}{rank}")


@cache
def piece_name_from_piece_type(piece_type: "PieceType") -> "PieceName":
    return PIECE_TYPE_TO_NAME[piece_type]


@cache
def piece_name_from_piece_role(piece_role: "PieceRole") -> "PieceName":
    return piece_name_from_piece_type(type_from_piece_role(piece_role))


@cache
def utf8_symbol_from_piece_type(piece_type: "PieceType") -> str:
    return PIECE_TYPE_TO_UNICODE[piece_type]


@cache
def utf8_symbol_from_piece_role(piece_role: "PieceRole") -> str:
    return utf8_symbol_from_piece_type(type_from_piece_role(piece_role))


def get_squares_with_pieces_that_can_move(board: chess.Board) -> frozenset["Square"]:
    return frozenset(
        cast("Square", chess.square_name(move.from_square))
        for move in board.legal_moves
    )


@lru_cache
def get_active_player_side_from_fen(fen: "FEN") -> "PlayerSide":
    return cast("PlayerSide", fen.split(" ")[1])


def get_active_player_side_from_chess_board(board: chess.Board) -> "PlayerSide":
    return "w" if board.turn else "b"


@lru_cache
def uci_move_squares(move: str) -> tuple["Square", "Square"]:
    return cast("Square", move[:2]), cast("Square", move[2:4])


@cache
def get_square_order(square: "Square") -> int:
    return SQUARES.index(square)


@cache
def player_side_to_chess_lib_color(player_side: "PlayerSide") -> chess.Color:
    return chess.WHITE if player_side == "w" else chess.BLACK


@cache
def chess_lib_color_to_player_side(color: chess.Color) -> "PlayerSide":
    return "w" if color == chess.WHITE else "b"
