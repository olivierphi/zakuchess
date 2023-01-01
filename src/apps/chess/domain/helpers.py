from typing import cast

import chess

from .types import PieceId, PieceIdsPerSquare, PiecesView, PieceSymbol, Square


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


def get_squares_with_pieces_that_can_move(board: chess.Board) -> set[Square]:
    return set(cast(Square, chess.square_name(move.from_square)) for move in board.legal_moves)
