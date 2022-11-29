from collections.abc import Sequence

import chess

from ..types import SquareName


def get_piece_available_targets(*, chess_board: chess.Board, piece_square: SquareName) -> Sequence[SquareName]:
    square_index = chess.parse_square(piece_square)
    print(
        f"select_piece({piece_square=})  :: {square_index=} :: board.turn={'white' if chess_board.turn else 'black'}"
    )
    result: list[SquareName] = []
    for move in chess_board.legal_moves:
        if move.from_square == square_index:
            result.append(chess.square_name(move.to_square))
    return result
