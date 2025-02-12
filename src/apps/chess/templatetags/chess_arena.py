from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django import template
from django.template import loader
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..components.chess_board import (
    SQUARE_COLOR_TAILWIND_CLASSES,
    chess_available_targets,
    chess_board,
    chess_bot_data,
    chess_last_move,
    chess_pieces,
)
from ..components.misc_ui import speech_bubble_container
from ..models import GameFactions

if TYPE_CHECKING:
    from django.template import RequestContext
    from django.utils.safestring import SafeString
    from dominate.tags import dom_tag

    from ..models import Faction
    from ..presenters import GamePresenter
    from ..types import FEN, PieceRole

register = template.Library()


def _render_tag_safe(tag: dom_tag) -> SafeString:
    return mark_safe(tag.render())


@register.simple_tag(takes_context=True)
@mark_safe
def chess_arena(
    context: RequestContext,
    *,
    game_presenter: GamePresenter,
    board_id: str,
    template_name: str = "chess/_chess_arena.html",
) -> str:
    request = context.get("request")

    chess_arena_elements = {
        "no_selection_url": game_presenter.urls.htmx_game_no_selection_url(
            board_id=board_id
        ),
        "chess_board": _render_tag_safe(
            chess_board(game_presenter=game_presenter, board_id=board_id)
        ),
        "chess_last_move": _render_tag_safe(
            chess_last_move(game_presenter=game_presenter, board_id=board_id)
        ),
        "chess_pieces": _render_tag_safe(
            chess_pieces(game_presenter=game_presenter, board_id=board_id)
        ),
        "chess_available_targets": _render_tag_safe(
            chess_available_targets(game_presenter=game_presenter, board_id=board_id)
        ),
        "chess_speech_bubble": _render_tag_safe(
            speech_bubble_container(game_presenter=game_presenter, board_id=board_id)
        ),
        "chess_bot_data": _render_tag_safe(chess_bot_data(board_id)),
    }

    sub_context = {
        **context.flatten(),
        **chess_arena_elements,
        "game_presenter": game_presenter,
        "board_id": board_id,
    }

    return loader.render_to_string(
        template_name,
        sub_context,
        request,
    )


@register.simple_tag
def unit_display_container(
    *,
    piece_role: PieceRole,
    factions: str,
    row_counter: int | None = None,
    additional_classes: str = "",
) -> str:
    from apps.chess.components.chess_board import chess_unit_display_with_ground_marker

    factions_seq = cast("list[Faction]", factions.split(","))
    factions_struct = GameFactions(w=factions_seq[0], b=factions_seq[1])

    unit_display = chess_unit_display_with_ground_marker(
        piece_role=piece_role,
        factions=factions_struct,
    )

    rounded_square_classes = (
        f"{SQUARE_COLOR_TAILWIND_CLASSES[row_counter % 2]} rounded-lg"
        if row_counter is not None
        else ""
    )

    return format_html(
        "<div class='{classes}'>{unit_display}</div>",
        classes=f"h-16 aspect-square {rounded_square_classes} {additional_classes}",
        unit_display=mark_safe(str(unit_display)),
    )


@register.filter
def turns_counter_from_fen(fen: FEN) -> int:
    """Returns the fullmove number, starting from 1"""
    return int(fen.split(" ")[-1])
