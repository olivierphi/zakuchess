import functools
import math
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.contrib.humanize.templatetags.humanize import ordinal
from django.urls import reverse
from dominate.tags import b, button, div, p
from dominate.util import raw

from apps.chess.components.svg_icons import ICON_SVG_CANCEL, ICON_SVG_CONFIRM

from ...models import PlayerGameOverState
from .common_styles import BUTTON_CANCEL_CLASSES, BUTTON_CLASSES, BUTTON_CONFIRM_CLASSES
from .svg_icons import (
    ICON_SVG_COG,
    ICON_SVG_LIGHT_BULB,
    ICON_SVG_RESTART,
    ICON_SVG_UNDO,
)

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
        cls=f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES} "
        "border-t-0 xl:border-2 xl:rounded-t-md",
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


def undo_confirmation_display(*, board_id: str) -> "dom_tag":
    htmx_attributes_confirm = {
        "data_hx_post": "".join(
            (
                reverse("daily_challenge:htmx_undo_last_move_do"),
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
            p("Undo your last move?"),
            b("⚠️ You will not be able to undo a move for today's challenge again."),
            cls="text-center",
        ),
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
                " ",
                ICON_SVG_CONFIRM,
                cls=BUTTON_CONFIRM_CLASSES,
                **htmx_attributes_confirm,
            ),
            button(
                "Cancel",
                " ",
                ICON_SVG_CANCEL,
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

    undo_button = _undo_button(game_presenter=game_presenter, board_id=board_id)
    retry_button = _retry_button(game_presenter=game_presenter, board_id=board_id)
    see_solution_button = _see_solution_button(board_id, full_width=True)
    user_prefs_button = _user_prefs_button(board_id)
    buttons = (
        undo_button,
        retry_button,
        see_solution_button,
        user_prefs_button,
    )

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
                *(div(bt, cls="px-3 md:px-5 xl:px-3") for bt in buttons),
                cls="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-2",
            ),
        ),
        cls="w-full",
    )


def _undo_button(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str
) -> "dom_tag":
    game_state = game_presenter.game_state
    can_undo: bool = game_presenter.is_preview or (
        game_state.current_attempt_turns_counter > 0
        and not game_state.undo_used
        and game_state.game_over != PlayerGameOverState.WON
    )

    htmx_attributes = (
        {
            "data_hx_post": "".join(
                (
                    reverse("daily_challenge:htmx_undo_last_move_ask_confirmation"),
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

    additional_attributes = {"disabled": True} if not can_undo else {}
    classes = _button_classes(disabled=not can_undo)

    return button(
        "Undo",
        " ",
        ICON_SVG_UNDO,
        cls=classes,
        title="Undo your last move",
        id=f"chess-board-undo-daily-challenge-{board_id}",
        **additional_attributes,
        **htmx_attributes,
    )


def _retry_button(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str
) -> "dom_tag":
    can_retry: bool = game_presenter.game_state.current_attempt_turns_counter > 0

    htmx_attributes = (
        {
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
        if can_retry
        else {}
    )

    additional_attributes = {"disabled": True} if not can_retry else {}
    classes = _button_classes(disabled=not can_retry)

    return button(
        "Retry",
        " ",
        ICON_SVG_RESTART,
        cls=classes,
        title="Try this daily challenge again, from the beginning",
        id=f"chess-board-restart-daily-challenge-{board_id}",
        **additional_attributes,
        **htmx_attributes,
    )


def _see_solution_button(
    board_id: str, *, full_width: bool, see_it_again: bool = False
) -> "dom_tag":
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

    classes = _button_classes(full_width=full_width)

    return button(
        "See solution",
        " ",
        ICON_SVG_LIGHT_BULB,
        cls=classes,
        title=title,
        id=f"chess-board-restart-daily-challenge-{board_id}",
        **htmx_attributes,
    )


def _user_prefs_button(board_id: str) -> "dom_tag":
    htmx_attributes = {
        "data_hx_get": reverse("daily_challenge:htmx_daily_challenge_modal_user_prefs"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    classes = _button_classes()

    return button(
        "Preferences",
        " ",
        ICON_SVG_COG,
        cls=classes,
        title="Edit preferences",
        id=f"chess-board-preferences-daily-challenge-{board_id}",
        **htmx_attributes,
    )


@functools.cache
def _button_classes(*, full_width: bool = True, disabled: bool = False) -> str:
    return " ".join(
        (
            BUTTON_CLASSES,
            ("w-full" if full_width else ""),
            (" opacity-50 cursor-not-allowed" if disabled else ""),
        )
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
                _see_solution_button(
                    board_id=board_id, full_width=False, see_it_again=True
                )
                if is_game_over
                else ""
            ),
            cls="w-full text-center",
        ),
        cls="w-full text-center",
    )
