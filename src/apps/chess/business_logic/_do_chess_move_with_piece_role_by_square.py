from typing import TYPE_CHECKING, NamedTuple, cast

from ..chess_helpers import (
    get_active_player_side_from_chess_board,
    get_active_player_side_from_fen,
)

if TYPE_CHECKING:
    import chess

    from ..types import (
        FEN,
        ChessInvalidStateException,
        ChessMoveResult,
        PieceRole,
        PieceRoleBySquare,
        PieceSymbol,
        Square,
    )


class ChessMoveWithPieceRoleBySquareResult(NamedTuple):
    move_result: "ChessMoveResult"
    piece_role_by_square: "PieceRoleBySquare"
    captured_piece: "PieceRole | None"


def do_chess_move_with_piece_role_by_square(
    *,
    from_: "Square",
    to: "Square",
    piece_role_by_square: "PieceRoleBySquare",
    fen: "FEN | None" = None,
    chess_board: "chess.Board | None" = None,
) -> ChessMoveWithPieceRoleBySquareResult:
    from ._do_chess_move import do_chess_move

    if (not fen and not chess_board) or (fen and chess_board):
        raise ValueError(
            "You must provide either a FEN string or a `chess.Board` object"
        )

    try:
        move_result = do_chess_move(
            fen=fen,
            chess_board=chess_board,
            from_=from_,
            to=to,
        )
    except ValueError as err:
        raise ChessInvalidStateException(f"Suspicious chess move: '{err}'") from err

    active_player_side = (
        get_active_player_side_from_fen(fen)
        if fen
        else get_active_player_side_from_chess_board(chess_board)  # type: ignore[arg-type]
    )
    piece_role_by_square = piece_role_by_square.copy()
    if promotion := move_result["promotion"]:
        # Let's promote that piece!
        piece_promotion = cast(
            "PieceSymbol", promotion.upper() if active_player_side == "w" else promotion
        )
        piece_role_by_square[from_] += piece_promotion  # type: ignore

    captured_piece: "PieceRole | None" = None
    if captured := move_result["captured"]:
        assert move_result["is_capture"]
        captured_piece = piece_role_by_square[captured]
        del piece_role_by_square[captured]  # this square is now empty

    for move_from, move_to in move_result["moves"]:
        piece_role_by_square[move_to] = piece_role_by_square[move_from]
        del piece_role_by_square[move_from]  # this square is now empty

    return ChessMoveWithPieceRoleBySquareResult(
        move_result, piece_role_by_square, captured_piece
    )
