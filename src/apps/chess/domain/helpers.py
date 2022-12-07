from collections.abc import Mapping
from typing import cast

import chess

from .types import PieceId, PieceIdsPerSquare, PiecesView, PieceSymbol, Square

KINGS_CASTLING: tuple[tuple[Square, Square], ...] = (
    # (king's previous quare, king's new square)
    ("e1", "g1"),
    ("e1", "c1"),
    ("e8", "g8"),
    ("e8", "c8"),
)

ROOK_SQUARE_AFTER_CASTLING: Mapping[Square, tuple[Square, Square]] = {
    # king new square: (rook previous square, rook new square)
    "g1": ("h1", "f1"),
    "c1": ("a1", "d1"),
    "g8": ("h8", "f8"),
    "c8": ("a8", "d8"),
}


def square_from_int(chess_lib_square: int) -> Square:
    return cast(Square, chess.square_name(chess_lib_square))


def pieces_view_from_chess_board(board: chess.Board, square_to_id_mapping: PieceIdsPerSquare) -> PiecesView:
    pieces_view_as_list: list[tuple[Square, PieceId, PieceSymbol]] = []
    for square, piece in board.piece_map().items():
        square_name = cast(Square, chess.square_name(square))
        symbol = cast(PieceSymbol, piece.symbol())
        pieces_view_as_list.append((square_name, square_to_id_mapping[square_name], symbol))
    # In order to get DOM elements that can be matched when we replace the board in the DOM and apply
    # CSS transitions to them, we need a constant sorting of our pieces, wherever they're moving.
    # --> we sort them by id!
    return {
        view_tuple[0]: PiecesView(id=view_tuple[1], piece=view_tuple[2])
        for view_tuple in sorted(pieces_view_as_list, key=lambda v: v[1])
    }
