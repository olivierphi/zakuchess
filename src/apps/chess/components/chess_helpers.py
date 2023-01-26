from functools import cache
from typing import TYPE_CHECKING, cast

from ..domain.consts import PIECE_TYPE_TO_NAME

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..domain.types import File, PieceRole, PieceSymbol, PieceType, PlayerSide, Rank, Square


_FILE_TO_TAILWIND_POSITIONING_CLASS: dict["File", str] = {
    "a": "translate-y-0/1",
    "b": "translate-y-1/1",
    "c": "translate-y-2/1",
    "d": "translate-y-3/1",
    "e": "translate-y-4/1",
    "f": "translate-y-5/1",
    "g": "translate-y-6/1",
    "h": "translate-y-7/1",
}
_RANK_TO_TAILWIND_POSITIONING_CLASS: dict["Rank", str] = {
    "1": "translate-x-0/1",
    "2": "translate-x-1/1",
    "3": "translate-x-2/1",
    "4": "translate-x-3/1",
    "5": "translate-x-4/1",
    "6": "translate-x-5/1",
    "7": "translate-x-6/1",
    "8": "translate-x-7/1",
}


@cache
def file_and_rank_from_square(square: "Square") -> tuple["File", "Rank"]:
    return cast(File, square[0]), cast("Rank", square[1])


@cache
def square_to_tailwind_classes(square: "Square") -> "Sequence[str]":
    file, rank = file_and_rank_from_square(square)
    return (
        _FILE_TO_TAILWIND_POSITIONING_CLASS[file],
        _RANK_TO_TAILWIND_POSITIONING_CLASS[rank],
    )


@cache
def piece_unit_classes(piece_role: "PieceRole") -> "Sequence[str]":
    classes = [f"bg-wesnoth-loyalists-{PIECE_TYPE_TO_NAME[piece_type(piece_role)]}"]
    player_side = piece_player_side(piece_role)
    if player_side == "b":
        classes.append("-scale-x-100")
    return classes


@cache
def piece_symbol(piece_role: "PieceRole") -> "PieceSymbol":
    return cast("PieceSymbol", piece_role[0])


@cache
def piece_type(piece_role: "PieceRole") -> "PieceType":
    return cast("PieceType", piece_symbol(piece_role).lower())


@cache
def piece_player_side(piece_role: "PieceRole") -> "PlayerSide":
    return "w" if piece_symbol(piece_role).isupper() else "b"