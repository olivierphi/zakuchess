from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, cast

import chess

from .consts import FILES, RANKS

if TYPE_CHECKING:
    from .types import (
        FEN,
        File,
        Move,
        MoveUCI,
        PieceName,
        PieceType,
        PlayerSide,
        Rank,
        Square,
    )

_PIECE_INT_TO_PIECE_TYPE: dict[int, PieceType] = {
    chess.PAWN: "p",
    chess.KNIGHT: "n",
    chess.BISHOP: "b",
    chess.ROOK: "r",
    chess.QUEEN: "q",
    chess.KING: "k",
}
_PIECE_TYPE_TO_NAME: dict[PieceType, PieceName] = {
    "p": "pawn",
    "n": "knight",
    "b": "bishop",
    "r": "rook",
    "q": "queen",
    "k": "king",
}

_PIECE_TYPE_TO_UNICODE: dict[PieceType, str] = {
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}


@cache
def chess_lib_square_to_square(chess_lib_square: int) -> Square:
    return cast("Square", chess.SQUARE_NAMES[chess_lib_square])


@cache
def chess_lib_piece_to_piece_type(chess_lib_piece: int) -> PieceType:
    # a bit hacky but that will do the job for now ^^
    return _PIECE_INT_TO_PIECE_TYPE[chess_lib_piece]


@cache
def player_side_other(player_side: PlayerSide) -> PlayerSide:
    return "w" if player_side == "b" else "b"


@cache
def file_and_rank_from_square(square: Square) -> tuple[File, Rank]:
    file, rank = square[0], square[1]
    # As the result is cached, we can allow ourselves some sanity checks
    # when Python's "optimization mode" is not turned on:
    assert file in FILES and rank in RANKS, f"square '{square}' is not valid"
    return cast("File", file), cast("Rank", rank)


@cache
def square_from_file_and_rank(file: File, rank: Rank) -> Square:
    # Inverse of the function above
    assert file in FILES, f"file '{file}' is not valid"
    assert rank in RANKS, f"rank '{rank}' is not valid"
    return cast("Square", f"{file}{rank}")


@cache
def piece_name_from_piece_type(piece_type: PieceType) -> PieceName:
    return _PIECE_TYPE_TO_NAME[piece_type]


@cache
def utf8_symbol_from_piece_type(piece_type: PieceType) -> str:
    return _PIECE_TYPE_TO_UNICODE[piece_type]


def get_active_player_side_from_fen(fen: FEN) -> PlayerSide:
    return cast("PlayerSide", fen.split(" ")[1])


def get_turns_counter_from_fen(fen: FEN) -> int:
    """Returns the fullmove number, starting from 1"""
    return int(fen.split(" ")[-1])


def get_active_player_side_from_chess_board(board: chess.Board) -> PlayerSide:
    return "w" if board.turn else "b"


def uci_to_move(move: MoveUCI) -> Move:
    return cast("Square", move[:2]), cast("Square", move[2:4])


def move_to_uci(move: Move) -> MoveUCI:
    # Inverse of the function above
    return cast("MoveUCI", f"{move[0]}{move[1]}")


@cache
def player_side_to_chess_lib_color(player_side: PlayerSide) -> chess.Color:
    return chess.WHITE if player_side == "w" else chess.BLACK


@cache
def chess_lib_color_to_player_side(color: chess.Color) -> PlayerSide:
    # Inverse of the function above
    return "w" if color == chess.WHITE else "b"
