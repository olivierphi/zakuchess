import functools
from typing import TYPE_CHECKING, cast

import chess

from apps.chess.chess_helpers import (
    chess_lib_color_to_player_side,
    chess_lib_square_to_square,
    team_member_role_from_piece_role,
)
from apps.chess.models import GameTeams, TeamMember

if TYPE_CHECKING:
    from apps.chess.models import GameFactions
    from apps.chess.types import (
        PieceRole,
        PieceRoleBySquare,
        PieceSymbol,
        PlayerSide,
        Square,
    )

# Since we cache the result of this function, we want to return an immutable object.
# --> instead of returning a PieceRoleBySquare dict, we return a tuple of tuples - from
# which we can easily re-create a PieceRoleBySquare dict.
PieceRoleBySquareTuple = tuple[tuple["Square", "PieceRole"], ...]


@functools.cache
def create_teams_and_piece_role_by_square_for_starting_position(
    factions: "GameFactions",
) -> "tuple[GameTeams, PieceRoleBySquareTuple]":
    # fmt: off
    piece_counters: dict["PieceSymbol", int | None] = {
        "P": 0, "R": 0, "N": 0, "B": 0, "Q": None, "K": None,
        "p": 0, "r": 0, "n": 0, "b": 0, "q": None, "k": None,
    }
    # fmt: on

    teams: "dict[PlayerSide, list[TeamMember]]" = {"w": [], "b": []}
    piece_role_by_square: "PieceRoleBySquare" = {}
    chess_board = chess.Board()
    for chess_square in chess.SQUARES:
        piece = chess_board.piece_at(chess_square)
        if not piece:
            continue

        player_side = chess_lib_color_to_player_side(piece.color)
        symbol = cast("PieceSymbol", piece.symbol())  # e.g. "P", "p", "R", "r"...
        if piece_counters[symbol]:
            piece_counters[symbol] += 1  # type: ignore[operator]
            piece_role = cast(
                "PieceRole", f"{symbol}{piece_counters[symbol]}"
            )  # e.g "P1", "r2"....
        else:
            piece_role = cast("PieceRole", symbol)  # e.g. "Q", "k"...

        team_member_role = team_member_role_from_piece_role(piece_role)
        team_member = TeamMember(
            role=team_member_role,
            name=("",),
            faction=factions.get_faction_for_side(player_side),
        )
        teams[player_side].append(team_member)

        square = chess_lib_square_to_square(chess_square)
        piece_role_by_square[square] = piece_role

    return (
        GameTeams(w=tuple(teams["w"]), b=tuple(teams["b"])),
        tuple(piece_role_by_square.items()),
    )
