import random
from typing import TYPE_CHECKING, Literal

from dominate.tags import a, button, div, h3, i, script, span
from dominate.util import raw

from .chess_helpers import square_to_square_center_tailwind_classes
from .svg_icons import ICON_SVG_CLOSE

if TYPE_CHECKING:
    from dominate.util import text as dominate_text

    from ..presenters import GamePresenter
    from ..types import PieceRole, Square


# tailwind name, hex value:
_SPEECH_BUBBLE_BACKGROUND_COLOR = ("bg-slate-900", "#0f172a")
_SPEECH_BUBBLE_TAIL_SIZE = 10  # px


if TYPE_CHECKING:
    from dominate.tags import dom_tag


# TODO: manage i18n


def modal_container(*, header: h3, body: div) -> "dom_tag":
    # Converted from https://flowbite.com/docs/components/modal/

    modal_header = div(
        header,
        button(
            ICON_SVG_CLOSE,
            span("Close modal", cls="sr-only"),
            type="button",
            onclick="closeModal()",
        ),
        cls="flex items-start justify-between p-4 border-b rounded-t",
    )

    modal_footer = div(
        i("A Zakuchess a day keeps the doctor away."),
        cls="text-sm text-center p-6 space-x-2 border-t border-gray-200 rounded-b",
    )

    modal_content = div(
        modal_header,
        body,
        modal_footer,
        cls="relative mt-8 bg-gray-950 rounded-lg shadow shadow-slate-950",
    )

    animation_start_class = "translate-y-16"
    animation_classes = (
        "transition-transform",
        "duration-500",
        "transform-gpu",
        animation_start_class,
    )

    return div(
        div(
            modal_content,
            cls=f"relative w-full mx-auto max-w-2xl max-h-full {' '.join(animation_classes)}",
            data_classes=f"remove {animation_start_class}:10ms",
        ),
        cls=" ".join(
            (
                "fixed top-0 left-0 right-0 z-50 w-full overflow-x-hidden overflow-y-auto",
                "md:inset-0 h-[calc(100%)] max-h-full",
                "bg-gray-900/75 p-1 text-slate-100 ",
            )
        ),
        id="modals-container",
    )


def speech_bubble_container(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> "dom_tag":
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
    text: "str | dominate_text",
    square: "Square",
    time_out: float | None,
    character_display: "PieceRole | None" = None,
    board_id: str,
    **extra_attrs: str,
) -> "dom_tag":
    from .chess_board import chess_character_display

    relative_position: Literal["left", "right"] = "right" if square[1] < "5" else "left"

    bubble_classes = (
        # Positioning:
        "absolute",
        "-top-10",
        "left-10" if relative_position == "right" else "right-10",
        # Size:
        "w-40",
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
            text,
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
        "bottom-1",
        "left-8" if relative_position == "right" else "right-8",
    )
    bubble_tail = div(
        "",
        cls=" ".join(bubble_tail_classes),
        style=" ".join(
            (
                # @link https://css-tricks.com/snippets/css/css-triangle/
                # We could do that using Tailwind, but it's just easier to use
                # good old CSS here...
                "border-top:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid transparent;",
                "border-bottom:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid transparent;",
                f"border-{'right' if relative_position == 'right' else 'left'}:",
                f"{_SPEECH_BUBBLE_TAIL_SIZE}px solid {_SPEECH_BUBBLE_BACKGROUND_COLOR[1]}",
            )
        ),
    )

    bubble_container_no_flickering_classes = ("hidden", "!block")
    bubble_container = div(
        bubble,
        bubble_tail,
        # We avoid an annoying flickering effect (still not sure why it happens thb)
        # by hiding this first and then showing it with JS:
        cls=f"relative drop-shadow-speech-bubble {bubble_container_no_flickering_classes[0]}",
        data_classes=f"add {bubble_container_no_flickering_classes[1]}:120ms",
    )

    outer_classes = [
        "absolute",
        "drop-shadow-lg",
        "opacity-90",
        *square_to_square_center_tailwind_classes(square),
    ]

    # Yawp, it's weak randomness, but it should be enough to differentiate between
    # 2 consecutive speech bubbles :-)
    speech_bubble_unique_id = str(random.randint(10_000, 99_999))

    hide_script = (
        script(
            raw(
                f"""setTimeout(closeSpeechBubble.bind(null, "{speech_bubble_unique_id}"), {int(time_out * 1000)})"""
            )
        )
        if time_out
        else ""
    )

    return div(
        bubble_container,
        hide_script,
        id=f"speech-container-{board_id}",
        cls=" ".join(outer_classes),
        data_speech_bubble_id=speech_bubble_unique_id,
        data_speech_bubble=True,
        **extra_attrs,
    )
