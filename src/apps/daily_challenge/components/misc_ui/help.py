import random
from functools import cache
from typing import TYPE_CHECKING, cast

from django.conf import settings
from dominate.tags import div, h4, p, span
from dominate.util import raw

from apps.chess.components.chess_board import SQUARE_COLOR_TAILWIND_CLASSES
from apps.chess.components.chess_helpers import chess_unit_symbol_class
from apps.chess.consts import PIECE_TYPE_TO_NAME
from apps.daily_challenge.components.misc_ui.common_styles import (
    BUTTON_BASE_HOVER_TEXT_COLOR,
    BUTTON_CLASSES,
)
from apps.daily_challenge.components.misc_ui.svg_icons import (
    ICON_SVG_COG,
    ICON_SVG_LIGHT_BULB,
    ICON_SVG_RESTART,
)

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from apps.chess.types import (
        Faction,
        Factions,
        PieceName,
        PieceRole,
        PieceType,
        PlayerSide,
        TeamMemberRole,
    )


_CHARACTER_TYPE_TIP: dict["PieceType", str] = {
    "p": "Characters with <b>swords</b>",
    "n": "<b>Mounted</b> characters",
    "b": "Characters with <b>a bow</b>",
    "r": "<b>Flying</b> characters",
    "q": "Characters with <b>a staff</b>",
    "k": "Characters wearing <b>heavy armors</b>",
}
_CHARACTER_TYPE_TIP_KEYS = tuple(_CHARACTER_TYPE_TIP.keys())

_CHARACTER_TYPE_ROLE_MAPPING: dict["PieceType", "TeamMemberRole"] = {
    "p": "p1",
    "n": "n1",
    "b": "b1",
    "r": "r1",
    "q": "q",
    "k": "k",
}


@cache
def help_content(
    *,
    challenge_solution_turns_count: int,
    factions_tuple: "tuple[tuple[PlayerSide, Faction], ...]",
) -> "dom_tag":
    # N.B. We use a tuple here for the factions, so they're hashable
    # and can be used as cached key

    spacing = "mb-3"
    factions = dict(factions_tuple)

    return raw(
        div(
            h4(
                "Welcome to this new daily challenge!",
                cls=f"{spacing} text-yellow-400 font-bold ",
            ),
            div(
                p(
                    raw(
                        "Today's challenge "
                        f"<b>can be solved in {challenge_solution_turns_count} turns</b>."
                    )
                ),
                cls=f"{spacing}",
            ),
            div(
                "Your pieces are the ones with a green circle, like these:",
                div(
                    unit_display_container(piece_role="N1", factions=factions),
                    unit_display_container(piece_role="Q", factions=factions),
                    cls="w-full flex justify-center gap-3",
                ),
                "Tap one of them to start playing.",
                cls=f"{spacing}",
            ),
            div(
                raw("You can <b>restart from the beginning</b> at any time, "),
                "by clicking the ",
                span(
                    "Retry",
                    ICON_SVG_RESTART,
                    cls=f"{BUTTON_CLASSES.replace(BUTTON_BASE_HOVER_TEXT_COLOR, '')} !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div(
                "If you can't solve today's challenge ",
                raw("you can decide to <b>see a solution</b>, by clicking the "),
                span(
                    "See solution",
                    ICON_SVG_LIGHT_BULB,
                    cls=f"{BUTTON_CLASSES} !inline-block !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div(
                raw("You can <b>customise some game settings</b>"),
                " - such as the speed of the game or the appearance of the board - via the ",
                span(
                    "Options",
                    ICON_SVG_COG,
                    cls=f"{BUTTON_CLASSES} !inline-block !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div("Good luck! 🙂", cls=f"p-3 {spacing} font-bold"),
            div(
                div(
                    span("🛡 Your troops", cls="text-yellow-400 font-bold"),
                    span(""),
                    span("The undead 💀", cls="text-yellow-400 font-bold"),
                    cls="flex w-full justify-between items-center",
                ),
                *(
                    chess_status_bar_tip(
                        factions=factions,
                        piece_type=piece_type,
                        additional_classes="h-20",
                        row_counter=i,
                    )
                    for i, piece_type in enumerate(_CHARACTER_TYPE_TIP_KEYS)
                ),
                cls="mt-2",
            ),
            cls="w-full text-center",
        ).render(pretty=settings.DEBUG)
    )


def chess_status_bar_tip(
    *,
    factions: "Factions",
    piece_type: "PieceType | None" = None,
    additional_classes: str = "",
    row_counter: int | None = None,
) -> "dom_tag":
    if piece_type is None:
        piece_type = random.choice(_CHARACTER_TYPE_TIP_KEYS)
    piece_name = PIECE_TYPE_TO_NAME[piece_type]
    unit_left_side_role = cast(
        "PieceRole", _CHARACTER_TYPE_ROLE_MAPPING[piece_type].upper()
    )
    unit_right_side_role = _CHARACTER_TYPE_ROLE_MAPPING[piece_type]
    unit_display_left = unit_display_container(
        piece_role=unit_left_side_role, factions=factions, row_counter=row_counter
    )
    unit_display_right = unit_display_container(
        piece_role=unit_right_side_role, factions=factions, row_counter=row_counter
    )

    return div(
        unit_display_left,
        div(
            character_type_tip(piece_type),
            chess_unit_symbol_display(player_side="w", piece_name=piece_name),
            cls="text-center",
        ),
        unit_display_right,
        cls=f"flex w-full justify-between items-center {additional_classes}",
    )


def unit_display_container(
    *, piece_role: "PieceRole", factions: "Factions", row_counter: int | None = None
) -> "dom_tag":
    from apps.chess.components.chess_board import chess_unit_display_with_ground_marker

    unit_display = chess_unit_display_with_ground_marker(
        piece_role=piece_role,
        factions=factions,
    )

    additional_classes = (
        f"{SQUARE_COLOR_TAILWIND_CLASSES[row_counter%2]} rounded-lg"
        if row_counter is not None
        else ""
    )

    return div(
        unit_display,
        cls=f"h-16 aspect-square {additional_classes}",
    )


def character_type_tip(piece_type: "PieceType") -> "dom_tag":
    return raw(
        f"{_CHARACTER_TYPE_TIP[piece_type]} are chess <b>{PIECE_TYPE_TO_NAME[piece_type]}s</b>"
    )


def chess_unit_symbol_display(
    *, player_side: "PlayerSide", piece_name: "PieceName"
) -> "dom_tag":
    classes = (
        "inline-block",
        "w-5",
        "align-text-bottom",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        chess_unit_symbol_class(player_side=player_side, piece_name=piece_name),
    )

    return span(
        cls=" ".join(classes),
    )
