from typing import TYPE_CHECKING, Literal
from urllib.parse import urlencode

from django.urls import reverse
from dominate.tags import button, div, dom_tag, span

if TYPE_CHECKING:
    from ...presenters import GamePresenter

BlockColor = Literal["grey", "green", "yellow", "red"]
PROGRESS_BAR_BLOCKS: dict[BlockColor, str] = {
    "grey": "⬜",
    "green": "🟩",
    "yellow": "🟨",
    "red": "🟥",
}
PROGRESS_BAR_BLOCKS_COUNT = 10


def chess_daily_challenge_bar(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    from ..chess_board import INFO_BARS_COMMON_CLASSES

    if game_presenter.restart_daily_challenge_ask_confirmation:
        inner_content = _restart_confirmation_display(board_id=board_id)
    else:
        inner_content = _current_state_display(game_presenter=game_presenter, board_id=board_id)

    return div(
        inner_content,
        id=f"chess-board-daily-challenge-bar-{board_id}",
        cls=f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES} border-t-0",
        **extra_attrs,
    )


def _restart_confirmation_display(*, board_id: str) -> dom_tag:
    htmx_attributes_confirm = {
        "data_hx_post": f"{reverse('chess:htmx_restart_daily_challenge_do')}?{urlencode({'board_id': board_id})}",
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }
    htmx_attributes_cancel = {
        "data_hx_get": f"{reverse('chess:htmx_game_no_selection')}?{urlencode({'board_id': board_id})}",
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }

    return div(
        span("Try this challenge again from the start?"),
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
    )


def _current_state_display(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:

    turns_total, turns_left, percentage_left, is_challenge_over = game_presenter.challenge_turns_left

    blocks_color: BlockColor = "green" if percentage_left >= 60 else ("yellow" if percentage_left >= 30 else "red")
    blocks: list[str] = []
    for i in range(PROGRESS_BAR_BLOCKS_COUNT):
        percentage = (i + 1) * 100 / PROGRESS_BAR_BLOCKS_COUNT
        if percentage > percentage_left:
            blocks_color = "grey"
        blocks.append(PROGRESS_BAR_BLOCKS[blocks_color])

    restart_button: dom_tag = span("")
    if not game_presenter.is_game_over and turns_left > 2:
        htmx_attributes = {
            "data_hx_post": f"{reverse('chess:htmx_restart_daily_challenge_ask_confirmation')}?{urlencode({'board_id': board_id})}",
            "data_hx_target": f"#chess-board-pieces-{board_id}",
            "data_hx_swap": "outerHTML",
        }
        restart_button = span(
            button(
                "↩️",
                title="Try this daily challenge again, from the start",
                id=f"chess-board-restart-daily-challenge-{board_id}",
                **htmx_attributes,
            ),
        )

    return div(
        div(f"Today's turns left: {turns_left}/{turns_total}", cls="w-full text-center"),
        div(
            span(
                "".join(blocks),
                cls="inline-block pl-3 pr-3",
            ),
            restart_button,
            cls="w-full text-center",
        ),
    )
