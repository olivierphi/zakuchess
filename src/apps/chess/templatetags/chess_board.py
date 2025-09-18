from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, TypeAlias

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from apps.chess.business_logic import FILES, RANKS

if TYPE_CHECKING:
    from django.utils.safestring import SafeString
    from apps.chess.game_state import GameState

register = template.Library()

_logger = logging.getLogger(__name__)

@register.simple_tag()
def chess_board_squares()->SafeString:
    squares:list[str] = []
    for file in FILES:
        for rank in RANKS:
            squares.append(f"""<div data-square="{file}{rank}">{file}{rank}</div>""")
    return mark_safe("\n".join(squares))

@register.simple_tag()
def chess_board_pieces(game_state:GameState)->SafeString:
    pieces:list[str] = []
    for square, piece in game_state.pieces.items():
        pieces.append(f"""<div id="piece-{game_state.id}-{piece.symbol()}" data-square="{square}">{piece.unicode_symbol()}</div>""")
    return mark_safe("\n".join(pieces))
