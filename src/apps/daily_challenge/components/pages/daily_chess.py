import functools
from string import Template
from typing import TYPE_CHECKING

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from dominate.tags import button, div, meta, script
from dominate.util import raw

from apps.chess.components.chess_board import (
    chess_arena,
    chess_available_targets,
    chess_last_move,
    chess_pieces,
)
from apps.chess.components.misc_ui import (
    reset_chess_engine_worker,
    speech_bubble_container,
)
from apps.webui.components.layout import page

from ..misc_ui.daily_challenge_bar import daily_challenge_bar
from ..misc_ui.status_bar import status_bar
from ..misc_ui.svg_icons import ICON_SVG_HELP, ICON_SVG_STATS

if TYPE_CHECKING:
    from typing import Literal

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
        _open_help_modal() if game_presenter.is_very_first_game else div(""),
        request=request,
        stats_button=_stats_button(),
        help_button=_help_button(),
        head_children=_open_graph_meta_tags(),
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
                div(
                    speech_bubble_container(
                        game_presenter=game_presenter,
                        board_id=board_id,
                    ),
                    id=f"chess-speech-container-{board_id}",
                    data_hx_swap_oob="innerHTML",
                ),
                *(
                    [reset_chess_engine_worker()]
                    if game_presenter.challenge_current_attempt_turns_counter == 0
                    else []
                ),
                *([_open_stats_modal()] if game_presenter.just_won else []),
            )
        )
    )


def _stats_button() -> "dom_tag":
    htmx_attributes = {
        "data_hx_get": reverse("daily_challenge:htmx_daily_challenge_modal_stats"),
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


def _help_button() -> "dom_tag":
    htmx_attributes = {
        "data_hx_get": reverse("daily_challenge:htmx_daily_challenge_modal_help"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return button(
        ICON_SVG_HELP,
        cls="block px-2 py-1 text-sm text-slate-50 hover:text-slate-400",
        title="How to play",
        id="help-button",
        **htmx_attributes,
    )


@functools.cache
def _open_stats_modal() -> "dom_tag":
    # We open the stats modal 2 seconds after the game is won.
    return _open_modal("stats", 2_000)


@functools.cache
def _open_help_modal() -> "dom_tag":
    # We open the stats modal 4 seconds after the bot played their first move.
    return _open_modal("help", 4_000)


_MODAL_TEMPLATE = Template(
    # Hacky? For sure 😅
    # (no XSS issue here though, as the variables don't come from the users)
    """{
        setTimeout(() => { htmx.trigger("#${MODAL_ID}-button", "click", {}) }, ${DELAY});
    }"""
)


def _open_modal(modal_id: "Literal['stats', 'help']", delay: int) -> "dom_tag":
    return div(
        script(
            raw(_MODAL_TEMPLATE.substitute(MODAL_ID=modal_id, DELAY=delay)),
        ),
        id="modals-container",
        data_hx_swap_oob="innerHTML",
    )


def _open_graph_meta_tags() -> "tuple[dom_tag, ...]":
    return (
        meta(
            property="og:image",
            content=static("daily_challenge/img/og-image-1200x630.png"),
        ),
        meta(property="og:image:type", content="image/png"),
        meta(property="og:image:width", content="1200"),
        meta(property="og:image:height", content="630"),
        meta(
            property="og:image:alt",
            content="The starting screen of a new ZakuChess daily challenge",
        ),
    )
