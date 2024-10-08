import random
from typing import TYPE_CHECKING, cast

import chess

from apps.chess.data.team_member_names import FIRST_NAMES, LAST_NAMES
from apps.chess.helpers import (
    chess_lib_color_to_player_side,
    chess_lib_square_to_square,
    player_side_other,
)

if TYPE_CHECKING:
    from apps.chess.types import (
        FEN,
        Faction,
        GameTeams,
        PieceRole,
        PieceRoleBySquare,
        PieceType,
        PlayerSide,
        TeamMember,
        TeamMemberRole,
    )

_CHESS_LIB_PIECE_TYPE_TO_PIECE_TYPE_MAPPING: dict[int, "PieceType"] = {
    chess.PAWN: "p",
    chess.KNIGHT: "n",
    chess.BISHOP: "b",
    chess.ROOK: "r",
    chess.QUEEN: "q",
    chess.KING: "k",
}


def set_daily_challenge_teams_and_pieces_roles(
    *,
    fen: "FEN",
    default_faction_w: "Faction" = "humans",
    default_faction_b: "Faction" = "undeads",
    bot_side: "PlayerSide" = "b",
    # TODO: allow partial customisation of team members?
    # custom_team_members: "GameTeams | None" = None,
) -> tuple["GameTeams", "PieceRoleBySquare"]:
    chess_board = chess.Board(fen)

    # fmt: off
    team_members_counters: dict["PlayerSide", dict["PieceType", list[int]]] = {
        #  - First int of the tuple is the current counter
        #  - Second int is the maximum value for that counter
        # (9 knights/bishops/rooks/queens on a player's side is quite an extreme case,
        # but it's theoretically possible via pawn promotions ^^)
        "w": {
            "p": [1, 8], "n": [1, 9], "b": [1, 9], "r": [1, 9], "q": [0, 9], "k": [0, 1]
        },
        "b": {
            "p": [1, 8], "n": [1, 9], "b": [1, 9], "r": [1, 9], "q": [0, 9], "k": [0, 1]
        },
    }
    # fmt: on

    piece_role_by_square: "PieceRoleBySquare" = {}

    piece_faction: dict["PlayerSide", "Faction"] = {
        "w": default_faction_w,
        "b": default_faction_b,
    }

    teams: "GameTeams" = {"w": [], "b": []}

    for chess_square, chess_piece in chess_board.piece_map().items():
        piece_player_side = chess_lib_color_to_player_side(chess_piece.color)
        piece_type = _CHESS_LIB_PIECE_TYPE_TO_PIECE_TYPE_MAPPING[chess_piece.piece_type]
        team_member_role_counter, piece_role_max_value = team_members_counters[
            piece_player_side
        ][piece_type]
        piece_role = cast(
            "PieceRole",
            (
                f"{piece_type}{team_member_role_counter}"
                if team_member_role_counter > 0
                else piece_type
            ),
        )
        team_member_role = cast(
            "TeamMemberRole",
            piece_role.upper() if piece_player_side == "w" else piece_role,
        )

        if team_member_role_counter > piece_role_max_value:
            raise ValueError(
                f"Cannot create more than {piece_role_max_value} pieces(s) "
                "in a game for type '{piece_type}'"
            )

        square = chess_lib_square_to_square(chess_square)
        piece_role_by_square[square] = team_member_role

        team_member: "TeamMember" = {
            "role": team_member_role,
            "name": "",  # will be filled below by `_set_character_names_for_non_bot_side`
            "faction": piece_faction[piece_player_side],
        }
        teams[piece_player_side].append(team_member)

        team_members_counters[piece_player_side][piece_type][0] += 1

    # Give a name to the player's team members
    _set_character_names_for_non_bot_side(teams, bot_side=bot_side)

    return teams, piece_role_by_square


def _set_character_names_for_non_bot_side(
    teams: "GameTeams", bot_side: "PlayerSide"
) -> None:
    player_side: "PlayerSide" = player_side_other(bot_side)
    player_team_members = teams[player_side]
    first_names = random.sample(FIRST_NAMES, k=len(player_team_members))
    last_names = random.sample(LAST_NAMES, k=len(player_team_members))
    for team_member in player_team_members:
        team_member["name"] = [first_names.pop(), last_names.pop()]
