from typing import TYPE_CHECKING

from dominate.tags import div, dom_tag
from dominate.util import raw

from .chess_helpers import square_to_square_center_tailwind_classes

if TYPE_CHECKING:
    from ..presenters import GamePresenter
    from ..types import Square


_SPEECH_BUBBLE_BACKGROUND_COLOR = ("bg-slate-50", "#f8fafc")  # tailwind name, hex value
_SPEECH_BUBBLE_TAIL_SIZE = 10  # px


def speech_bubble_container(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> dom_tag:
    if speech_bubble_data := game_presenter.speech_bubble:
        return speech_bubble(
            text=speech_bubble_data.text,
            square=speech_bubble_data.square,
            time_out=speech_bubble_data.time_out,
            board_id=board_id,
            **extra_attrs,
        )

    return div(id=f"speech-container-{board_id}", **extra_attrs)


def speech_bubble(
    *, text: str, square: "Square", time_out: int, board_id: str, **extra_attrs: str
) -> dom_tag:
    bubble_classes = (
        # Positioning:
        "absolute",
        "bottom-7",
        "left-0",
        # Size:
        "min-w-40",
        "p-1 ",
        # Cosmetics:
        _SPEECH_BUBBLE_BACKGROUND_COLOR[0],
        "text-slate-900",
        "text-sm",
        "font-medium",
        "rounded-md",
    )
    bubble = div(
        raw(text),
        cls=" ".join(bubble_classes),
    )

    bubble_tail_classes = (
        "absolute",
        "w-0",
        "h-0",
        "bottom-5",
        "left-1",
    )
    bubble_tail = div(
        "",
        cls=" ".join(bubble_tail_classes),
        style=" ".join(
            (
                # @link https://css-tricks.com/snippets/css/css-triangle/
                "border-left:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid transparent;",
                "border-right:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid transparent;",
                "border-top:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid {_SPEECH_BUBBLE_BACKGROUND_COLOR[1]}",
            )
        ),
    )

    bubble_container = div(
        bubble,
        bubble_tail,
        cls="relative",
        data_remove_me=f"{time_out}s",
    )

    outer_classes = (
        "absolute",
        "drop-shadow-lg",
        "opacity-90",
        *square_to_square_center_tailwind_classes(square),
    )

    return div(
        bubble_container,
        id=f"speech-container-{board_id}",
        cls=" ".join(outer_classes),
        # @link https://htmx.org/extensions/remove-me/
        data_hx_ext="remove-me",
        **extra_attrs,
    )
