from chess import UNICODE_PIECE_SYMBOLS
from django import template

from apps.chess.domain import PieceSymbol, PlayerCode

register = template.Library()


@register.filter
def player_code_from_symbol(symbol: PieceSymbol) -> PlayerCode:
    return "w" if symbol.upper() == symbol else "b"


@register.filter
def piece_unicode_from_symbol(symbol: PieceSymbol) -> str:
    return UNICODE_PIECE_SYMBOLS[symbol]


@register.filter(name="abs")
def abs_(number: int | float) -> int | float:
    return abs(number)
