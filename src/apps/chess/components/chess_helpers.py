from functools import cache
from typing import TYPE_CHECKING

from apps.chess.consts import PIECE_TYPE_TO_NAME
from apps.chess.helpers import (
    file_and_rank_from_square,
    player_side_from_piece_role,
    type_from_piece_role,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.chess.types import (
        Faction,
        Factions,
        File,
        PieceName,
        PieceRole,
        PlayerSide,
        Rank,
        Square,
    )

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

_PIECE_UNITS_CLASSES: "dict[Faction, dict[PieceName, str]]" = {
    # We need Tailwind to see these classes, so that it bundles them in the final CSS file.
    "humans": {
        "pawn": "bg-humans-pawn",
        "knight": "bg-humans-knight",
        "bishop": "bg-humans-bishop",
        "rook": "bg-humans-rook",
        "queen": "bg-humans-queen",
        "king": "bg-humans-king",
    },
    "undeads": {
        "pawn": "bg-undeads-pawn",
        "knight": "bg-undeads-knight",
        "bishop": "bg-undeads-bishop",
        "rook": "bg-undeads-rook",
        "queen": "bg-undeads-queen",
        "king": "bg-undeads-king",
    },
}

_PIECE_SYMBOLS_CLASSES: "dict[PlayerSide, dict[PieceName, str]]" = {
    # Ditto.
    "w": {
        "pawn": "bg-w-pawn",
        "knight": "bg-w-knight",
        "bishop": "bg-w-bishop",
        "rook": "bg-w-rook",
        "queen": "bg-w-queen",
        "king": "bg-w-king",
    },
    "b": {
        "pawn": "bg-b-pawn",
        "knight": "bg-b-knight",
        "bishop": "bg-b-bishop",
        "rook": "bg-b-rook",
        "queen": "bg-b-queen",
        "king": "bg-b-king",
    },
}


@cache
def square_to_tailwind_classes(square: "Square") -> "Sequence[str]":
    file, rank = file_and_rank_from_square(square)
    return (
        _FILE_TO_TAILWIND_POSITIONING_CLASS[file],
        _RANK_TO_TAILWIND_POSITIONING_CLASS[rank],
    )


def piece_character_classes(
    *, piece_role: "PieceRole", factions: "Factions"
) -> "Sequence[str]":
    return _piece_character_classes_for_factions(
        piece_role=piece_role, factions_tuple=tuple(factions.items())
    )


@cache
def _piece_character_classes_for_factions(
    *, piece_role: "PieceRole", factions_tuple: "tuple[tuple[PlayerSide, Faction], ...]"
) -> "Sequence[str]":
    # N.B. We use a tuple here for the factions, so they're hashable and can be used as cached key
    piece_name = PIECE_TYPE_TO_NAME[type_from_piece_role(piece_role)]
    player_side = player_side_from_piece_role(piece_role)
    factions_dict = dict(factions_tuple)
    faction = factions_dict[player_side]
    classes = [_PIECE_UNITS_CLASSES[faction][piece_name]]
    player_side = player_side_from_piece_role(piece_role)
    if player_side == "b":
        classes.append("-scale-x-100")
    return classes


@cache
def chess_unit_symbol_class(
    *, player_side: "PlayerSide", piece_name: "PieceName"
) -> str:
    return _PIECE_SYMBOLS_CLASSES[player_side][piece_name]
