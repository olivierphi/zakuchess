from chess import UNICODE_PIECE_SYMBOLS
from django import template

from apps.chess.domain.types import PieceSymbol, PlayerSide

register = template.Library()


@register.filter
def player_code_from_symbol(symbol: PieceSymbol) -> str:
    return PlayerSide.W if symbol.upper() == symbol else PlayerSide.B


@register.filter
def piece_unicode_from_symbol(symbol: PieceSymbol) -> str:
    return UNICODE_PIECE_SYMBOLS[symbol]


@register.filter(name="abs")
def abs_(number: int | float) -> int | float:
    return abs(number)
