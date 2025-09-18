from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, TypeAlias

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from apps.chess.business_logic import FILES, RANKS

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from django.utils.safestring import SafeString

register = template.Library()

_logger = logging.getLogger(__name__)

@register.simple_tag()
def chess_board_squares()->SafeString:
    squares:list[str] = []
    for file in FILES:
        for rank in RANKS:
            squares.append(f"""<div class="square" data-square="{file}{rank}">{file}{rank}</div>""")
    return mark_safe("\n".join(squares))
