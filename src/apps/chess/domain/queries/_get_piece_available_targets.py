from collections.abc import Sequence

import chess

from ..helpers import square_from_int
from ..types import Square


def get_piece_available_targets(*, chess_board: chess.Board, piece_square: Square) -> Sequence[Square]:
    square_index = chess.parse_square(piece_square)
    print(
        f"select_piece({piece_square=})  :: {square_index=} :: board.turn={'white' if chess_board.turn else 'black'}"
    )
    result: list[Square] = []
    for move in chess_board.legal_moves:
        if move.from_square == square_index:
            result.append(square_from_int(move.to_square))
    return result
