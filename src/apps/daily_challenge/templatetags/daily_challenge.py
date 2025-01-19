from __future__ import annotations

import functools
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.webui.components.atoms.buttons import zc_button, zc_header_icon_button
from apps.webui.components.misc_ui.svg_icons import ICON_SVG_COG, ICON_SVG_HELP

from ..components.misc_ui.svg_icons import (
    ICON_SVG_LIGHT_BULB,
    ICON_SVG_RESTART,
    ICON_SVG_STATS,
    ICON_SVG_UNDO,
)
from ..models import PlayerGameOverState

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.template import RequestContext
    from dominate.tags import dom_tag


# TODO: i18n

register = template.Library()


@register.simple_tag
@mark_safe
def header_stats_button() -> str:
    htmx_attributes = {
        "data_hx_get": reverse("daily_challenge:htmx_daily_challenge_modal_stats"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return zc_header_icon_button(
        icon=ICON_SVG_STATS,
        title="Visualise your stats for daily challenges",
        id_="stats-button",
        htmx_attributes=htmx_attributes,
    ).render()


@register.simple_tag
@mark_safe
def header_help_button() -> str:
    htmx_attributes = {
        "data_hx_get": reverse("daily_challenge:htmx_daily_challenge_modal_help"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return zc_header_icon_button(
        icon=ICON_SVG_HELP,
        title="How to play",
        id_="help-button",
        htmx_attributes=htmx_attributes,
    ).render()


@register.simple_tag
@mark_safe
def header_user_prefs_button() -> str:
    htmx_attributes = {
        "data_hx_get": reverse("webui:htmx_modal_user_prefs"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return zc_header_icon_button(
        icon=ICON_SVG_COG,
        title="Edit preferences",
        id_="user-prefs-button",
        htmx_attributes=htmx_attributes,
    ).render()


@register.simple_tag(takes_context=True)
@mark_safe
def companion_bar_undo_button(context: RequestContext) -> str:
    game_presenter = context["game_presenter"]
    board_id = context["board_id"]

    game_state = game_presenter.game_state
    can_undo: bool = game_presenter.is_preview or (
        game_state.current_attempt_turns_counter > 0
        and not game_state.undo_used
        and game_state.game_over != PlayerGameOverState.WON
    )

    htmx_attrs = (
        {
            "data_hx_get": "".join(
                (
                    # TODO: Django 5.2: use new `reverse()` features
                    reverse("daily_challenge:htmx_undo_last_move_confirmation_dialog"),
                    "?",
                    urlencode({"board_id": board_id}),
                )
            ),
            "data_hx_target": f"#chess-board-daily-challenge-bar-{board_id}",
            "data_hx_swap": "innerHTML",
        }
        if can_undo
        else {}
    )

    additional_attrs = {"disabled": True} if not can_undo else {}
    classes = _button_classes(disabled=not can_undo)

    return _wrap_top_companion_bar_button(
        zc_button(
            "Undo",
            svg_icon=ICON_SVG_UNDO,
            button_type="action",
            title="Undo your last move",
            id_=f"chess-board-undo-daily-challenge-{board_id}",
            htmx_attrs=htmx_attrs,
            extra_classes=classes,
            extra_attrs=additional_attrs,
        )
    )


@register.simple_tag(takes_context=True)
@mark_safe
def companion_bar_retry_button(context: RequestContext) -> str:
    game_presenter = context["game_presenter"]
    board_id = context["board_id"]

    can_retry: bool = game_presenter.game_state.current_attempt_turns_counter > 0

    htmx_attrs = (
        {
            "data_hx_get": "".join(
                (
                    reverse(
                        "daily_challenge:htmx_restart_daily_challenge_confirmation_dialog"
                    ),
                    "?",
                    urlencode({"board_id": board_id}),
                )
            ),
            "data_hx_target": f"#chess-board-daily-challenge-bar-{board_id}",
            "data_hx_swap": "innerHTML",
        }
        if can_retry
        else {}
    )

    additional_attrs = {"disabled": True} if not can_retry else {}
    classes = _button_classes(disabled=not can_retry)

    return _wrap_top_companion_bar_button(
        zc_button(
            "Retry",
            svg_icon=ICON_SVG_RESTART,
            button_type="action",
            extra_classes=classes,
            title="Try this daily challenge again, from the beginning",
            id_=f"chess-board-restart-daily-challenge-{board_id}",
            extra_attrs=additional_attrs,
            htmx_attrs=htmx_attrs,
        )
    )


@register.simple_tag(takes_context=True)
@mark_safe
def companion_bar_see_solution_button(
    context: RequestContext, *, full_width: bool, see_it_again: bool = False
) -> str:
    board_id = context["board_id"]

    target_route = (
        "daily_challenge:htmx_see_daily_challenge_solution_do"
        if see_it_again
        else "daily_challenge:htmx_see_daily_challenge_solution_confirmation_dialog"
    )
    target_route_http_method = "post" if see_it_again else "get"
    target_selector = (
        f"#chess-board-pieces-{board_id}"
        if see_it_again
        else f"#chess-board-daily-challenge-bar-{board_id}"
    )
    title = (
        "See this solution again"
        if see_it_again
        else "Give up for today, and see a solution"
    )

    htmx_attrs = {
        f"data_hx_{target_route_http_method}": "".join(
            (
                reverse(target_route),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": target_selector,
        "data_hx_swap": "innerHTML",
    }

    classes = _button_classes(full_width=full_width)

    return _wrap_top_companion_bar_button(
        zc_button(
            "See solution",
            svg_icon=ICON_SVG_LIGHT_BULB,
            button_type="action",
            extra_classes=classes,
            title=title,
            id_=f"chess-board-restart-daily-challenge-{board_id}",
            htmx_attrs=htmx_attrs,
        )
    )


@register.simple_tag(takes_context=True)
@mark_safe
def companion_bar_user_prefs_button(context: RequestContext) -> str:
    board_id = context["board_id"]

    htmx_attrs = {
        "data_hx_get": reverse("webui:htmx_modal_user_prefs"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    classes = _button_classes()

    return _wrap_top_companion_bar_button(
        zc_button(
            "Preferences",
            svg_icon=ICON_SVG_COG,
            button_type="action",
            extra_classes=classes,
            title="Edit preferences",
            id_=f"chess-board-preferences-daily-challenge-{board_id}",
            htmx_attrs=htmx_attrs,
        )
    )


def _wrap_top_companion_bar_button(button: dom_tag) -> str:
    return f'<div class="px-3 py-1 md:px-5 xl:px-3">{button}</div>'


@functools.cache
def _button_classes(
    *, full_width: bool = True, disabled: bool = False
) -> Sequence[str]:
    return (
        ("w-full" if full_width else ""),
        (" opacity-50 cursor-not-allowed" if disabled else ""),
    )
