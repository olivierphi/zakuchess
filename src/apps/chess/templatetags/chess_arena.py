from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.template import loader
from django.utils.safestring import mark_safe

from ..components.chess_board import (
    chess_available_targets,
    chess_board,
    chess_bot_data,
    chess_last_move,
    chess_pieces,
)
from ..components.misc_ui import speech_bubble_container

if TYPE_CHECKING:
    from django.template import RequestContext
    from django.utils.safestring import SafeString
    from dominate.tags import dom_tag

    from ..presenters import GamePresenter

register = template.Library()


def _render_tag_safe(tag: dom_tag) -> SafeString:
    return mark_safe(tag.render())


@register.simple_tag(takes_context=True)
@mark_safe
def chess_arena(
    context: RequestContext,
    *,
    template_name: str,
    game_presenter: GamePresenter,
    board_id: str,
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
