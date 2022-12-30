from typing import TYPE_CHECKING, cast

from ..domain.consts import PIECE_ROLE_TO_NAME
from ..domain.types import PieceRole, PlayerSide

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..domain.types import Square, PieceView


def square_to_tailwind_classes(square: "Square") -> "Sequence[str]":
    file, rank = square
    return (
        _FILE_TO_TAILWIND_POSITIONING_CLASS[file],
        _RANK_TO_TAILWIND_POSITIONING_CLASS[rank],
    )


def piece_unit_classes(piece_view: "PieceView") -> "Sequence[str]":
    piece_role = cast(PieceRole, piece_view["piece"].lower())
    classes = [f"bg-wesnoth-loyalists-{PIECE_ROLE_TO_NAME[piece_role]}"]
    player_side = piece_player_side(piece_view)
    if player_side == "b":
        classes.append("-scale-x-100")
    return classes


def piece_player_side(piece_view: "PieceView") -> PlayerSide:
    return "w" if piece_view["piece"].isupper() else "b"


_FILE_TO_TAILWIND_POSITIONING_CLASS = {
    "a": "top-0/8",
    "b": "top-1/8",
    "c": "top-2/8",
    "d": "top-3/8",
    "e": "top-4/8",
    "f": "top-5/8",
    "g": "top-6/8",
    "h": "top-7/8",
}
_RANK_TO_TAILWIND_POSITIONING_CLASS = {
    "1": "left-0/8",
    "2": "left-1/8",
    "3": "left-2/8",
    "4": "left-3/8",
    "5": "left-4/8",
    "6": "left-5/8",
    "7": "left-6/8",
    "8": "left-7/8",
}
