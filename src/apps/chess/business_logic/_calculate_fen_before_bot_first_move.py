from typing import TYPE_CHECKING

import chess

from ..helpers import chess_lib_color_to_player_side

if TYPE_CHECKING:
    from .types import FEN, PlayerSide


def calculate_fen_before_bot_first_move(
    *, fen_after_first_move: "FEN", bot_first_move: str, bot_side: "PlayerSide"
) -> "FEN":
    """
    Calculate the FEN of the chess board before the bot's first move.
    Raises a ValueError if the bot's first move is invalid.
    """

    # Ok folks, we're going back to the previous turn:
    chess_board = chess.Board(fen_after_first_move)
    chess_board.turn = not chess_board.turn

    # ...and put back that piece where it was:
    move = chess.Move.from_uci(bot_first_move)
    piece = chess_board.piece_at(move.to_square)

    if piece is None:
        raise ValueError(
            f"Invalid bot first move '{bot_first_move}': "
            f"no piece at square '{chess.SQUARE_NAMES[move.from_square]}'"
        )

    piece_player_side = chess_lib_color_to_player_side(piece.color)
    if piece_player_side != bot_side:
        raise ValueError(
            f"Invalid bot first move '{bot_first_move}': "
            f"piece at square '{move.from_square}' is not from bot side '{bot_side}'"
        )

    # Now let's go back in time and rewind that first move...
    chess_board.remove_piece_at(move.to_square)
    chess_board.set_piece_at(move.from_square, piece)

    # ...and check if the bot can actually make that move:
    legal_moves = tuple(chess_board.legal_moves)
    if move not in legal_moves:
        raise ValueError(
            f"Invalid bot first move '{bot_first_move}': "
            f"move is not part of the legal chess moves '{[move.uci() for move in  legal_moves]}'"
        )

    return chess_board.fen()
