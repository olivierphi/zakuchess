import functools
from typing import TYPE_CHECKING

from django.conf import settings
from django.urls import reverse
from dominate.tags import button, div, script
from dominate.util import raw

from apps.chess.components.chess_board import (
    chess_arena,
    chess_available_targets,
    chess_last_move,
    chess_pieces,
)
from apps.chess.components.misc_ui import speech_bubble_container
from apps.webui.components.layout import page

from ..misc_ui import daily_challenge_bar, status_bar
from ..misc_ui.svg_icons import ICON_SVG_STATS

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag

    from ...presenters import DailyChallengeGamePresenter

# These are the top-level components returned by our Django Views.


def daily_challenge_page(
    *,
    game_presenter: "DailyChallengeGamePresenter",
    request: "HttpRequest",
    board_id: str,
) -> str:
    return page(
        chess_arena(
            game_presenter=game_presenter,
            board_id=board_id,
            status_bars=[
                daily_challenge_bar(game_presenter=game_presenter, board_id=board_id),
                status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
            ],
        ),
        request=request,
        stats_button=_stats_button(),
    )


def daily_challenge_moving_parts_fragment(
    *,
    game_presenter: "DailyChallengeGamePresenter",
    request: "HttpRequest",
    board_id: str,
) -> str:
    return "\n".join(
        (
            dom_tag.render(pretty=settings.DEBUG)
            for dom_tag in (
                chess_pieces(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
                chess_available_targets(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                (
                    chess_last_move(
                        game_presenter=game_presenter,
                        board_id=board_id,
                        data_hx_swap_oob="outerHTML",
                    )
                    if game_presenter.refresh_last_move
                    else div("")
                ),
                daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                speech_bubble_container(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                _open_stats_modal() if game_presenter.just_won else div(""),
            )
        )
    )


def _stats_button() -> "dom_tag":
    htmx_attributes = {
        "data_hx_get": "".join((reverse("daily_challenge:htmx_daily_challenge_stats"))),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return button(
        ICON_SVG_STATS,
        cls="block px-2 py-1 text-sm text-slate-50 hover:text-slate-400",
        title="Visualise your stats for daily challenges",
        id="stats-button",
        **htmx_attributes,
    )


@functools.cache
def _open_stats_modal() -> "dom_tag":
    return div(
        script(
            raw(
                """setTimeout(() => { htmx.trigger("#stats-button", "click", {}) }, 2000)"""
            ),
        ),
        id="modals-container",
        data_hx_swap_oob="innerHTML",
    )
