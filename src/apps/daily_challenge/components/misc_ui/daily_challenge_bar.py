from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.contrib.humanize.templatetags.humanize import ordinal
from django.urls import reverse
from dominate.tags import button, div, dom_tag
from dominate.util import raw

from .common_styles import BUTTON_CLASSES
from .svg_icons import ICON_SVG_RESTART

if TYPE_CHECKING:
    from ...presenters import DailyChallengeGamePresenter


def daily_challenge_bar(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str, **extra_attrs: str
) -> dom_tag:
    from apps.chess.components.chess_board import INFO_BARS_COMMON_CLASSES

    if game_presenter.restart_daily_challenge_ask_confirmation:
        inner_content = _restart_confirmation_display(board_id=board_id)
    else:
        inner_content = _current_state_display(
            game_presenter=game_presenter, board_id=board_id
        )

    return div(
        inner_content,
        id=f"chess-board-daily-challenge-bar-{board_id}",
        cls=f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES} border-t-0",
        **extra_attrs,
    )


def _restart_confirmation_display(*, board_id: str) -> dom_tag:
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

    return div(
        div(
            "Retry today's challenge from the start?",
            cls="text-center",
        ),
        div(
            button(
                "Confirm",
                cls="inline-block pl-3 pr-3 font-bold text-yellow-400 hover:text-yellow-200",
                **htmx_attributes_confirm,
            ),
            button(
                "Cancel",
                cls="inline-block pl-3 pr-3 font-bold text-lime-400 hover:text-lime-200",
                **htmx_attributes_cancel,
            ),
            cls="text-center",
        ),
    )


def _current_state_display(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str
) -> dom_tag:
    turns_counter = game_presenter.game_state.turns_counter
    attempts_counter = game_presenter.game_state.attempts_counter
    current_attempt_turns = game_presenter.game_state.current_attempt_turns_counter

    restart_button = _restart_button(board_id)

    return div(
        div(
            raw(
                " - ".join(
                    (
                        f"<b>{ordinal(attempts_counter+1)}</b> attempt",
                        f"turn <b>#{current_attempt_turns+1}</b>",
                    )
                )
            ),
            cls="text-center",
        ),
        div(
            (
                raw(f"<b>{turns_counter}</b> turns overall")
                if attempts_counter > 0
                else ""
            ),
            restart_button,
            cls="text-center",
        ),
        cls="w-full",
    )


def _restart_button(board_id: str) -> dom_tag:
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
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }

    return button(
        "restart ",
        ICON_SVG_RESTART,
        cls=BUTTON_CLASSES,
        title="Try this daily challenge again, from the start",
        id=f"chess-board-restart-daily-challenge-{board_id}",
        **htmx_attributes,
    )
