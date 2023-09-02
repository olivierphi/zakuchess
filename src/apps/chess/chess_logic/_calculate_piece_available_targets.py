from typing import TYPE_CHECKING

import chess

from apps.chess.helpers import square_from_int

if TYPE_CHECKING:
    from apps.chess.business_logic.types import Square


def calculate_piece_available_targets(*, chess_board: chess.Board, piece_square: "Square") -> frozenset["Square"]:
    square_index = chess.parse_square(piece_square)
    result: list["Square"] = []
    for move in chess_board.legal_moves:
        if move.from_square == square_index:
            result.append(square_from_int(move.to_square))
    return frozenset(result)
