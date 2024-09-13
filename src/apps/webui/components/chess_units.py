import random
from typing import TYPE_CHECKING, cast

from dominate.tags import div, span
from dominate.util import raw

from apps.chess.components.chess_board import SQUARE_COLOR_TAILWIND_CLASSES
from apps.chess.components.chess_helpers import chess_unit_symbol_class
from apps.chess.consts import PIECE_TYPE_TO_NAME

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from apps.chess.models import GameFactions
    from apps.chess.types import (
        PieceName,
        PieceRole,
        PieceType,
        PlayerSide,
        TeamMemberRole,
    )

CHARACTER_TYPE_TIP: dict["PieceType", str] = {
    # TODO: i18n
    "p": "Characters with <b>swords</b>",
    "n": "<b>Mounted</b> characters",
    "b": "Characters with <b>a bow</b>",
    "r": "<b>Flying</b> characters",
    "q": "Characters with <b>a staff</b>",
    "k": "Characters wearing <b>heavy armors</b>",
}
_CHARACTER_TYPE_TIP_KEYS = tuple(CHARACTER_TYPE_TIP.keys())

_CHARACTER_TYPE_ROLE_MAPPING: dict["PieceType", "TeamMemberRole"] = {
    "p": "p1",
    "n": "n1",
    "b": "b1",
    "r": "r1",
    "q": "q",
    "k": "k",
}


def chess_status_bar_tip(
    *,
    factions: "GameFactions",
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
    *, piece_role: "PieceRole", factions: "GameFactions", row_counter: int | None = None
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
        f"{CHARACTER_TYPE_TIP[piece_type]} are chess <b>{PIECE_TYPE_TO_NAME[piece_type]}s</b>"
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
