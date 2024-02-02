import random
from functools import cache
from typing import TYPE_CHECKING, cast

from django.conf import settings
from dominate.tags import div, h4, span
from dominate.util import raw

from apps.chess.components.chess_helpers import chess_unit_symbol_class
from apps.chess.consts import PIECE_TYPE_TO_NAME

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
    challenge_total_turns: int,
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
                "Your pieces are the ones with a green circle, like these one:",
                div(
                    unit_display_container(piece_role="N1", factions=factions),
                    unit_display_container(piece_role="Q", factions=factions),
                    cls="w-full flex justify-center gap-3",
                ),
                # div(
                #     div("", cls="relative z-20 font-bold"),
                #     chess_unit_ground_marker(player_side="w"),
                #     cls="inline-block relative whitespace-nowrap",
                # ),
                # br(),
                "Tap one of them to start playing.",
                cls=f"{spacing}",
            ),
            div(
                raw(
                    f"You have <b>{challenge_total_turns}</b> "
                    "turns to win this challenge."
                ),
                cls=f"{spacing}",
            ),
            div("Good luck! 🙂", cls=f"{spacing}"),
            div(
                [
                    chess_status_bar_tip(
                        factions=factions,
                        piece_type=piece_type,
                        additional_classes="h-20",
                    )
                    for piece_type in _CHARACTER_TYPE_TIP_KEYS
                ],
                cls="mt-2",
            ),
            # script(raw(_FIRST_TURN_INTRO_SCRIPT.substitute({"board_id": board_id}))),
            cls="w-full text-center",
        ).render(pretty=settings.DEBUG)
    )


def chess_status_bar_tip(
    *,
    factions: "Factions",
    piece_type: "PieceType | None" = None,
    additional_classes: str = "",
) -> "dom_tag":
    if piece_type is None:
        piece_type = random.choice(_CHARACTER_TYPE_TIP_KEYS)
    piece_name = PIECE_TYPE_TO_NAME[piece_type]
    unit_left_side_role = cast(
        "PieceRole", _CHARACTER_TYPE_ROLE_MAPPING[piece_type].upper()
    )
    unit_right_side_role = _CHARACTER_TYPE_ROLE_MAPPING[piece_type]
    unit_display_left = unit_display_container(
        piece_role=unit_left_side_role, factions=factions
    )
    unit_display_right = unit_display_container(
        piece_role=unit_right_side_role, factions=factions
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
    *, piece_role: "PieceRole", factions: "Factions"
) -> "dom_tag":
    from apps.chess.components.chess_board import chess_unit_display_with_ground_marker

    unit_display = chess_unit_display_with_ground_marker(
        piece_role=piece_role,
        factions=factions,
    )

    return div(
        unit_display,
        cls="h-16 aspect-square",
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
