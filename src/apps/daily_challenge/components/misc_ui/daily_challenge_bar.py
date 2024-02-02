from typing import TYPE_CHECKING, Literal
from urllib.parse import urlencode

from django.contrib.humanize.templatetags.humanize import ordinal
from django.urls import reverse
from dominate.tags import button, div, dom_tag, span
from dominate.util import raw

from .common_styles import BUTTON_CLASSES
from .svg_icons import ICON_SVG_RESTART

if TYPE_CHECKING:
    from ...presenters import DailyChallengeGamePresenter

BlockColor = Literal["grey", "green", "yellow", "red"]
PROGRESS_BAR_BLOCKS: dict[BlockColor, str] = {
    "grey": "⬜",
    "green": "🟩",
    "yellow": "🟨",
    "red": "🟥",
}
PROGRESS_BAR_BLOCKS_COUNT = 10


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

    (
        attempts_counter,
        current_attempt_turns,
        turns_total,
        turns_left,
        percentage_left,
        time_s_up,
    ) = game_presenter.challenge_turns_state

    blocks, danger = _challenge_turns_left_display_with_blocks(percentage_left)

    restart_button: dom_tag = span("")
    if not time_s_up:
        restart_button = _restart_button(board_id)

    turns_left_display = (
        f"""<b class="text-rose-600">{turns_left}</b>""" if danger else turns_left
    )

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
            div(
                raw(f"Today's turns left: {turns_left_display}/{turns_total}"),
                cls="text-center",
            ),
            div(
                blocks,
                restart_button,
                cls="flex justify-center items-center",
            ),
        ),
        cls="w-full",
    )


def _challenge_turns_left_display_with_blocks(
    percentage_left: int,
) -> tuple[dom_tag, bool]:
    blocks_color: BlockColor = (
        "green"
        if percentage_left >= 60
        else ("yellow" if percentage_left >= 30 else "red")
    )
    blocks: list[str] = []
    current_block_color: BlockColor = blocks_color
    for i in range(PROGRESS_BAR_BLOCKS_COUNT):
        percentage = (i + 1) * 100 / PROGRESS_BAR_BLOCKS_COUNT
        if percentage > percentage_left:
            current_block_color = "grey"
        blocks.append(PROGRESS_BAR_BLOCKS[current_block_color])

    return (
        span("".join(blocks)),
        blocks_color == "red",
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
