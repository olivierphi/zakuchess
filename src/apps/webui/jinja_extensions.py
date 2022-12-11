from typing import TYPE_CHECKING

from chess import UNICODE_PIECE_SYMBOLS

from apps.chess.domain.consts import PIECES_ROLE_BY_STARTING_SQUARE

if TYPE_CHECKING:
    from apps.chess.domain.types import PieceSymbol, PlayerSide, Square, TeamMemberRole


def _piece_unicode_from_symbol(value: "PieceSymbol") -> str:
    return UNICODE_PIECE_SYMBOLS[value]


def _player_side_from_piece(value: "PieceSymbol") -> "PlayerSide":
    return "w" if value.upper() == value else "b"


def _player_side_from_starting_square(starting_square: "Square") -> "PlayerSide":
    return "w" if starting_square[1] in ("1", "2") else "b"


def _team_member_role_from_starting_square(starting_square: "Square") -> "TeamMemberRole":
    return PIECES_ROLE_BY_STARTING_SQUARE[starting_square]


# Will be used by our "project.jinja2" module:
filters = {
    "piece_unicode_from_symbol": _piece_unicode_from_symbol,
    "player_side_from_piece": _player_side_from_piece,
    "team_member_role_from_starting_square": _team_member_role_from_starting_square,
}
