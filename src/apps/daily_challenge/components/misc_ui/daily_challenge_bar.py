import math
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.contrib.humanize.templatetags.humanize import ordinal
from django.urls import reverse
from dominate.tags import b, button, div, p
from dominate.util import raw

from .common_styles import BUTTON_CANCEL_CLASSES, BUTTON_CLASSES, BUTTON_CONFIRM_CLASSES
from .svg_icons import ICON_SVG_LIGHT_BULB, ICON_SVG_RESTART

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...presenters import DailyChallengeGamePresenter


def daily_challenge_bar(
    *,
    game_presenter: "DailyChallengeGamePresenter | None",
    board_id: str,
    inner_content: "dom_tag | None" = None,
    **extra_attrs: str,
) -> "dom_tag":
    from apps.chess.components.chess_board import INFO_BARS_COMMON_CLASSES

    if not inner_content:
        assert game_presenter is not None
        inner_content = _current_state_display(
            game_presenter=game_presenter, board_id=board_id
        )

    return div(
        inner_content,
        id=f"chess-board-daily-challenge-bar-{board_id}",
        cls=f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES} border-t-0",
        **extra_attrs,
    )


def retry_confirmation_display(*, board_id: str) -> "dom_tag":
    htmx_attributes_confirm = {
        "data_hx_post": "".join(
            (
                reverse("daily_challenge:htmx_restart_daily_challenge_do"),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }
    htmx_attributes_cancel = {
        "data_hx_get": "".join(
            (
                reverse("daily_challenge:htmx_game_no_selection"),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }

    return _confirmation_dialog(
        question=div("Retry today's challenge from the start?", cls="text-center"),
        htmx_attributes_confirm=htmx_attributes_confirm,
        htmx_attributes_cancel=htmx_attributes_cancel,
    )


def see_solution_confirmation_display(*, board_id: str) -> "dom_tag":
    htmx_attributes_confirm = {
        "data_hx_post": "".join(
            (
                reverse("daily_challenge:htmx_see_daily_challenge_solution_do"),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }
    htmx_attributes_cancel = {
        "data_hx_get": "".join(
            (
                reverse("daily_challenge:htmx_game_no_selection"),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }

    return _confirmation_dialog(
        question=div(
            p("Give up for today, and see a solution?"),
            b("⚠️ You will not be able to try today's challenge again."),
            cls="text-center",
        ),
        htmx_attributes_confirm=htmx_attributes_confirm,
        htmx_attributes_cancel=htmx_attributes_cancel,
    )


def _confirmation_dialog(
    *,
    question: "dom_tag",
    htmx_attributes_confirm: dict[str, str],
    htmx_attributes_cancel: dict[str, str],
) -> "dom_tag":
    return div(
        question,
        div(
            button(
                "Confirm",
                cls=BUTTON_CONFIRM_CLASSES,
                **htmx_attributes_confirm,
            ),
            button(
                "Cancel",
                cls=BUTTON_CANCEL_CLASSES,
                **htmx_attributes_cancel,
            ),
            cls="text-center",
        ),
    )


def _current_state_display(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str
) -> "dom_tag":
    if game_presenter.solution_index is not None:
        return _see_solution_mode_display(
            game_presenter=game_presenter, board_id=board_id
        )

    retry_button = _retry_button(board_id)
    see_solution_button = _see_solution_button(board_id)

    return div(
        div(
            raw(
                f"<b>{ordinal(game_presenter.challenge_attempts_counter+1)}</b> attempt: "
                f"turn <b>#{game_presenter.challenge_current_attempt_turns_counter+1}</b>"
            ),
            cls="text-center",
        ),
        div(
            div(
                retry_button,
                see_solution_button,
                cls="flex justify-center items-center",
            ),
        ),
        cls="w-full",
    )


def _retry_button(board_id: str) -> "dom_tag":
    htmx_attributes = {
        "data_hx_post": "".join(
            (
                reverse(
                    "daily_challenge:htmx_restart_daily_challenge_ask_confirmation"
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-daily-challenge-bar-{board_id}",
        "data_hx_swap": "innerHTML",
    }

    return button(
        "retry",
        ICON_SVG_RESTART,
        cls=BUTTON_CLASSES,
        title="Try this daily challenge again, from the beginning",
        id=f"chess-board-restart-daily-challenge-{board_id}",
        **htmx_attributes,
    )


def _see_solution_button(board_id: str, *, see_it_again: bool = False) -> "dom_tag":
    target_route = (
        "daily_challenge:htmx_see_daily_challenge_solution_do"
        if see_it_again
        else "daily_challenge:htmx_see_daily_challenge_solution_ask_confirmation"
    )
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

    htmx_attributes = {
        "data_hx_post": "".join(
            (
                reverse(target_route),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": target_selector,
        "data_hx_swap": "innerHTML",
    }

    return button(
        "see solution",
        ICON_SVG_LIGHT_BULB,
        cls=BUTTON_CLASSES,
        title=title,
        id=f"chess-board-restart-daily-challenge-{board_id}",
        **htmx_attributes,
    )


def _see_solution_mode_display(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str
) -> "dom_tag":
    assert game_presenter.game_state.solution_index is not None

    is_game_over = game_presenter.is_game_over
    turns_display = math.floor(game_presenter.game_state.solution_index / 2) + 1

    return div(
        (
            p("You are currently seeing a solution, " " and can't make any more moves.")
            if not is_game_over
            else ""
        ),
        p(
            (
                raw("This solution ended the game in " f"<b>{turns_display} turns</b>.")
                if is_game_over
                else raw(f"Turn <b>{turns_display}</b>.")
            ),
            cls="text-center",
        ),
        (
            p(
                "You can see that solution again:",
                cls="w-full text-center",
            )
            if is_game_over
            else ""
        ),
        p(
            (
                _see_solution_button(board_id=board_id, see_it_again=True)
                if is_game_over
                else ""
            ),
            cls="w-full text-center",
        ),
        cls="w-full text-center",
    )
