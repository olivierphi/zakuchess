from functools import cache
from typing import TYPE_CHECKING

from ..domain.consts import PIECE_TYPE_TO_NAME
from ..domain.helpers import file_and_rank_from_square, player_side_from_piece_role, type_from_piece_role

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..domain.types import File, PieceName, PieceRole, PlayerSide, Rank, Square, SquareColor

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
def square_to_tailwind_classes(square: "Square") -> "Sequence[str]":
    file, rank = file_and_rank_from_square(square)
    return (
        _FILE_TO_TAILWIND_POSITIONING_CLASS[file],
        _RANK_TO_TAILWIND_POSITIONING_CLASS[rank],
    )


@cache
def piece_unit_classes(piece_role: "PieceRole") -> "Sequence[str]":
    classes = [f"bg-wesnoth-loyalists-{PIECE_TYPE_TO_NAME[type_from_piece_role(piece_role)]}"]
    player_side = player_side_from_piece_role(piece_role)
    if player_side == "b":
        classes.append("-scale-x-100")
    return classes


@cache
def chess_unit_symbol_url(*, player_side: "PlayerSide", piece_name: "PieceName") -> str:
    return f"/static/chess/symbols/{player_side}-{piece_name}.svg"


@cache
def chess_square_color(square: "Square") -> "SquareColor":
    file = int(square[1])
    return "light" if (file % 2 == 0 if square[0] in ("a", "c", "e", "g") else file % 2 == 1) else "dark"
