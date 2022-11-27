from collections.abc import Mapping

import chess

from .domain import PieceId, PieceIdsPerSquare, PiecesView, PieceSymbol, SquareName

ROOK_SQUARE_AFTER_CASTLING: Mapping[SquareName, tuple[SquareName, SquareName]] = {
    # king new square: (rook previous square, rook new square)
    "g1": ("h1", "f1"),
    "c1": ("a1", "d1"),
    "g8": ("h8", "f8"),
    "c8": ("a8", "d8"),
}


def pieces_view_from_chess_board(board: chess.Board, square_to_id_mapping: PieceIdsPerSquare) -> PiecesView:
    pieces_view_as_list: list[tuple[SquareName, PieceId, PieceSymbol]] = []
    for square, piece in board.piece_map().items():
        square_name = chess.square_name(square)
        pieces_view_as_list.append((square_name, square_to_id_mapping[square_name], piece.symbol()))
    # In order to get DOM elements that can be matched by Django Unicorn and CSS transitions we need
    # a constant sorting of our pieces, wherever they're moving.
    # --> we sort them by id!
    return {
        view_tuple[0]: PiecesView(id=view_tuple[1], piece=view_tuple[2])
        for view_tuple in sorted(pieces_view_as_list, key=lambda v: v[1])
    }
