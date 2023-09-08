from typing import TYPE_CHECKING

import chess

from ..helpers import chess_lib_color_to_player_side

if TYPE_CHECKING:
    from apps.chess.types import FEN, PlayerSide


def calculate_fen_before_move(
    *, fen_after_move: "FEN", move_uci: str, moving_player_side: "PlayerSide"
) -> "FEN":
    """
    Calculate the FEN of the chess board before the given move.
    Raises a ValueError if the move is invalid.
    """

    # Ok folks, we're going back to the previous turn:
    chess_board = chess.Board(fen_after_move)
    chess_board.turn = not chess_board.turn

    # ...and put back that piece where it was:
    move = chess.Move.from_uci(move_uci)
    piece = chess_board.piece_at(move.to_square)

    if piece is None:
        pieces_map = {
            chess.SQUARE_NAMES[sq]: piece.symbol()
            for sq, piece in chess_board.piece_map().items()
        }
        raise ValueError(
            f"Invalid bot first move '{move_uci}': "
            f"no piece at square '{chess.SQUARE_NAMES[move.from_square]}'."
            f"Pieces map: {pieces_map}"
        )

    piece_player_side = chess_lib_color_to_player_side(piece.color)
    if piece_player_side != moving_player_side:
        raise ValueError(
            f"Invalid bot first move '{move_uci}': "
            f"piece at square '{move.from_square}' is not "
            f"from player side '{moving_player_side}'"
        )

    # Now let's go back in time and rewind that first move...
    chess_board.remove_piece_at(move.to_square)
    chess_board.set_piece_at(move.from_square, piece)

    # ...and check if the bot can actually make that move:
    legal_moves = tuple(chess_board.legal_moves)
    if move not in legal_moves:
        raise ValueError(
            f"Invalid bot first move '{move_uci}': "
            "move is not part of the legal chess moves "
            f"'{[move.uci() for move in  legal_moves]}'. "
            f"Previous turn FEN: {chess_board.fen()}"
        )

    return chess_board.fen()
