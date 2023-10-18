from typing import TYPE_CHECKING

from dominate.tags import a, div, dom_tag
from dominate.util import raw

from .chess_helpers import square_to_square_center_tailwind_classes

if TYPE_CHECKING:
    from ..presenters import GamePresenter
    from ..types import PieceRole, Square


# tailwind name, hex value:
_SPEECH_BUBBLE_BACKGROUND_COLOR = ("bg-slate-900", "#0f172a")
_SPEECH_BUBBLE_TAIL_SIZE = 10  # px


def speech_bubble_container(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> dom_tag:
    if speech_bubble_data := game_presenter.speech_bubble:
        return speech_bubble(
            game_presenter=game_presenter,
            text=speech_bubble_data.text,
            square=speech_bubble_data.square,
            time_out=speech_bubble_data.time_out,
            character_display=speech_bubble_data.character_display,
            board_id=board_id,
            **extra_attrs,
        )

    return div(id=f"speech-container-{board_id}", **extra_attrs)


def speech_bubble(
    *,
    game_presenter: "GamePresenter",
    text: str,
    square: "Square",
    time_out: int,
    character_display: "PieceRole | None" = None,
    board_id: str,
    **extra_attrs: str,
) -> dom_tag:
    from .chess_board import chess_character_display

    bubble_classes = (
        # Positioning:
        "absolute",
        "bottom-7",
        "left-0",
        # TODO: if the bubble is too close to the right edge of the screen,
        #  we should move it to the left a bit (the tail can stay where it is).
        # Size:
        "min-w-40",
        "p-2 ",
        # Cosmetics:
        _SPEECH_BUBBLE_BACKGROUND_COLOR[0],
        "text-amber-400",
        "text-sm",
        "font-medium",
        "rounded-md",
    )

    character_display_tag: dom_tag = (
        div(
            chess_character_display(
                game_presenter=game_presenter, piece_role=character_display
            ),
            cls="w-1/2 mx-auto",
        )
        if character_display
        else raw("")
    )

    bubble = div(
        div(
            raw(text),
            cls="text-center",
        ),
        character_display_tag,
        div(
            a(
                "close [x]",
                href="javascript:closeSpeechBubble()",
                cls="text-slate-100 text-xs italic pointer-events-auto",
            ),
            cls="text-right mt-2",
        ),
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
                # We could do that using Tailwind, but it's just easier to use
                # good old CSS here...
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
        cls="relative drop-shadow-speech-bubble",
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
        data_speech_bubble=True,
        **extra_attrs,
    )
