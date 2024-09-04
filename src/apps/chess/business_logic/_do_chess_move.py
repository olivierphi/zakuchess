from functools import lru_cache
from typing import TYPE_CHECKING, Literal, cast

import chess

from apps.chess.helpers import (
    chess_lib_piece_to_piece_type,
    file_and_rank_from_square,
    square_from_file_and_rank,
)
from apps.chess.types import (
    ChessInvalidMoveException,
    ChessMoveResult,
    GameOverDescription,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from apps.chess.types import FEN, GameEndReason, MoveTuple, PlayerSide, Rank, Square

_CHESS_COLOR_TO_PLAYER_SIDE_MAPPING: "Mapping[chess.Color, PlayerSide]" = {
    True: "w",
    False: "b",
}

_CHESS_OUTCOME_TO_GAME_END_REASON_MAPPING: "Mapping[chess.Termination, GameEndReason]" = {
    chess.Termination.CHECKMATE: "checkmate",
    chess.Termination.STALEMATE: "stalemate",
    chess.Termination.INSUFFICIENT_MATERIAL: "insufficient_material",
    chess.Termination.SEVENTYFIVE_MOVES: "seventyfive_moves",
    chess.Termination.THREEFOLD_REPETITION: "threefold_repetition",
    chess.Termination.FIVEFOLD_REPETITION: "fivefold_repetition",
    chess.Termination.FIFTY_MOVES: "fifty_moves",
}

_CastlingPossibleFrom = Literal["e1", "e1", "e8", "e8"]
_CastlingPossibleTo = Literal["g1", "c1", "g8", "c8"]

_CASTLING_KING_MOVES: tuple[tuple[_CastlingPossibleFrom, _CastlingPossibleTo], ...] = (
    # (king's previous square, king's new square) tuples:
    ("e1", "g1"),
    ("e1", "c1"),
    ("e8", "g8"),
    ("e8", "c8"),
)

_CASTLING_ROOK_MOVE: "Mapping[_CastlingPossibleTo, tuple[Square, Square]]" = {
    # {king new square: (rook previous square, rook new square)} dict:
    "g1": ("h1", "f1"),
    "c1": ("a1", "d1"),
    "g8": ("h8", "f8"),
    "c8": ("a8", "d8"),
}

_EN_PASSANT_CAPTURED_PIECES_RANK_CONVERSION: dict["Rank", "Rank"] = {
    # if a pawn was captured by en passant targeting a6, its position on the board
    # before at the moment it's been captured was a5:
    "6": "5",
    # same for the other side of the board:
    "3": "4",
}


@lru_cache(maxsize=512)
def do_chess_move(*, fen: "FEN", from_: "Square", to: "Square") -> ChessMoveResult:
    moves: list["MoveTuple"] = []
    captured: "Square | None" = None

    chess_board = chess.Board(fen)
    chess_from = chess.parse_square(from_)
    chess_to = chess.parse_square(to)

    current_piece = chess_board.piece_at(chess_from)
    if not current_piece:
        raise ValueError(f"No pieces on the selected square '{from_}'; fen='{fen}'")

    is_promotion = current_piece.piece_type == chess.PAWN and to[1] in ("1", "8")
    promotion = chess.QUEEN if is_promotion else None
    # TODO: allow the user to choose the promotion piece?
    chess_move = chess.Move(
        from_square=chess_from,
        to_square=chess_to,
        promotion=promotion,
    )
    board_legal_moves = frozenset(chess_board.legal_moves)
    if chess_move not in board_legal_moves:
        raise ChessInvalidMoveException(
            f"Invalid move '{from_}{to}' for FEN '{fen}' - "
            f"can only be one of {board_legal_moves}"
        )

    targeted_piece = chess_board.piece_at(chess_to)
    is_en_passant = chess_board.has_legal_en_passant() and chess_board.is_en_passant(
        chess_move
    )
    is_capture = targeted_piece is not None or is_en_passant

    previous_castling_rights = chess_board.castling_rights
    chess_board.push(chess_move)

    # Record that piece's move:
    moves.append((from_, to))

    # Record the capture, if any:
    if is_capture:
        if is_en_passant:
            # Jeez, "en passant" is more complicated to handle than it looks 😅
            to_square_file, to_square_rank = file_and_rank_from_square(to)
            en_passant_captured_pawn_square = square_from_file_and_rank(
                to_square_file,
                _EN_PASSANT_CAPTURED_PIECES_RANK_CONVERSION[to_square_rank],
            )
            # Ok, we determined the position of the pawn captured by the "en passant"
            # so now we can record that capture:
            captured = en_passant_captured_pawn_square
        else:
            captured = to  # the piece at the target square was simply captured

    # Specific cases:
    is_castling = False
    if (
        not is_capture
        and current_piece.piece_type == chess.KING
        and chess_board.castling_rights != previous_castling_rights
    ):
        king_movement = (from_, to)
        if king_movement in _CASTLING_KING_MOVES:
            # A King just castled!
            is_castling = True
            # Record that rook's move:
            rook_previous_square, rook_new_square = _CASTLING_ROOK_MOVE[
                cast(_CastlingPossibleTo, to)
            ]
            moves.append((rook_previous_square, rook_new_square))

    # Check the game's outcome:
    outcome = chess_board.outcome()
    if outcome:
        winner = (
            _CHESS_COLOR_TO_PLAYER_SIDE_MAPPING[outcome.winner]
            if outcome.winner
            else None
        )
        win_reason = _CHESS_OUTCOME_TO_GAME_END_REASON_MAPPING[outcome.termination]
    else:
        winner = None
        win_reason = None

    new_fen = chess_board.fen()

    domain_promotion = (
        None if promotion is None else chess_lib_piece_to_piece_type(promotion)
    )
    game_over = (
        GameOverDescription(winner=winner, reason=win_reason) if win_reason else None
    )

    return ChessMoveResult(
        fen=new_fen,
        moves=moves,
        is_capture=is_capture,
        captured=captured,
        is_castling=is_castling,
        promotion=domain_promotion,
        game_over=game_over,
    )
