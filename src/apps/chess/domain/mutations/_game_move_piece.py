from collections.abc import Mapping
from typing import TYPE_CHECKING, NamedTuple, cast

import chess
from django.core.exceptions import SuspiciousOperation

from ...models import Game

if TYPE_CHECKING:
    from ..types import PieceRoleBySquare, Square


class PieceMovementResult(NamedTuple):
    is_promotion: bool
    # game_over: bool


_KINGS_CASTLING: tuple[tuple["Square", "Square"], ...] = (
    # (king's previous square, king's new square) tuples:
    ("e1", "g1"),
    ("e1", "c1"),
    ("e8", "g8"),
    ("e8", "c8"),
)

_ROOK_SQUARE_AFTER_CASTLING: Mapping["Square", tuple["Square", "Square"]] = {
    # {king new square: (rook previous square, rook new square)} dict:
    "g1": ("h1", "f1"),
    "c1": ("a1", "d1"),
    "g8": ("h8", "f8"),
    "c8": ("a8", "d8"),
}


def game_move_piece(*, game: Game, from_square: "Square", to_square: "Square") -> PieceMovementResult:
    # TODO: validate against the board's legal moves, since Python Chess doesn't do that for us
    board = chess.Board(fen=game.fen)
    current_piece = board.piece_at(chess.parse_square(from_square))
    if not current_piece:
        raise SuspiciousOperation(f"No pieces on the selected square '{from_square}'")
    if current_piece.color != board.turn:
        raise SuspiciousOperation()
    team_member_role_by_square = cast("PieceRoleBySquare", game.piece_role_by_square)
    current_piece_role = team_member_role_by_square[from_square]
    targeted_piece = board.piece_at(chess.parse_square(to_square))  # # noqa: F841
    # print(
    #     f"board.turn={'white' if board.turn else 'black'} "
    #     f":: move_piece_to({to_square=}) "
    #     f":: from {from_square} :: {current_piece_id=} {targeted_piece=}"
    # )
    is_promotion = current_piece.piece_type == chess.PAWN and to_square[1] in ("1", "8")

    # @link https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
    # @link https://en.wikipedia.org/wiki/Universal_Chess_Interface
    move_uci_piece_symbol = "".join(
        [
            "",  # """ if current_piece.piece_type == chess.PAWN else current_piece.symbol().upper(),
            from_square,
            "",  # """ if targeted_piece is None else "x",
            to_square,
            # Promotion to Queen?
            # TODO: allow the user to choose the promotion piece?
            "q" if is_promotion else "",
        ]
    )
    previous_castling_rights = board.castling_rights
    board.push_uci(move_uci_piece_symbol)

    del team_member_role_by_square[from_square]
    team_member_role_by_square[to_square] = current_piece_role

    # Specific cases:
    if current_piece.piece_type == chess.KING and board.castling_rights != previous_castling_rights:
        king_movement = (from_square, to_square)
        if king_movement in _KINGS_CASTLING:
            # Our King just castled!
            # We also have to update the Rook's data in our `pieces_id_per_square` mapping
            target_rook_previous_square, target_rook_new_square = _ROOK_SQUARE_AFTER_CASTLING[to_square]
            target_rook_id = team_member_role_by_square[target_rook_previous_square]
            team_member_role_by_square[target_rook_new_square] = target_rook_id
            del team_member_role_by_square[target_rook_previous_square]

    # Right, let's update that model!
    game.fen = board.fen()
    game.active_player = "w" if board.turn else "b"
    game.piece_role_by_square = team_member_role_by_square
    game.save(update_fields=("fen", "active_player", "piece_role_by_square", "updated_at"))

    return PieceMovementResult(is_promotion=is_promotion)
