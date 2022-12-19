import chess

from ..helpers import square_from_int
from ..types import Square


def get_piece_available_targets(*, chess_board: chess.Board, piece_square: Square) -> set[Square]:
    square_index = chess.parse_square(piece_square)
    result: set[Square] = set()
    for move in chess_board.legal_moves:
        if move.from_square == square_index:
            result.add(square_from_int(move.to_square))
    return result
