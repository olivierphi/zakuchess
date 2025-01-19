from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from django import template
from django.utils.safestring import mark_safe

from apps.chess.components.chess_board import INFO_BARS_COMMON_CLASSES

if TYPE_CHECKING:
    from collections.abc import Mapping

register = template.Library()

CompanionBarPosition = Literal["top", "bottom"]


@register.simple_block_tag  # type: ignore
def chess_arena_companion_bar(
    content: str,
    *,
    position: CompanionBarPosition,
    board_id: str,
    extra_attrs: Mapping[str, str | bool] | None = None,
    htmx_attrs: Mapping[str, str | bool] | None = None,
    id_pattern: str | None = None,
):
    attributes = {
        **(extra_attrs or {}),
        **(htmx_attrs or {}),
    }
    if id_pattern:
        attributes["id"] = id_pattern.format(board_id=board_id)

    classes = (
        f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES}"
    )
    match position:
        case "top":
            classes += " border-t-0 xl:border-2 xl:rounded-t-md"
        case "bottom":
            classes += " border-t-0 rounded-b-md"

    return mark_safe(
        f'<div class="{classes}" {" ".join(f"{key}={value}" for key, value in attributes.items())}>'
        f"{content}"
        "</div>"
    )
