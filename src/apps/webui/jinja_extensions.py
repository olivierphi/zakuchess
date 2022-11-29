from chess import UNICODE_PIECE_SYMBOLS

from apps.chess.domain.types import PieceSymbol


def _piece_unicode_from_symbol(value: PieceSymbol) -> str:
    return UNICODE_PIECE_SYMBOLS[value]


def _player_side_from_piece(value: PieceSymbol) -> str:
    return "w" if value.upper() == value else "b"


# Will be used by our "project.jinja2" module:
filters = {
    "piece_unicode_from_symbol": _piece_unicode_from_symbol,
    "player_side_from_piece": _player_side_from_piece,
}
