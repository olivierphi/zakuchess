import random
from typing import TYPE_CHECKING, cast

import chess

from ...components.chess_helpers import chess_lib_color_to_player_side
from ...models import DailyChallenge
from ..data.team_member_names import FIRST_NAMES, LAST_NAMES
from ..helpers import square_from_int
from ..queries import calculate_fen_before_bot_first_move

if TYPE_CHECKING:
    from ..dto import GameTeams, TeamMember
    from ..types import FEN, Faction, PieceRole, PieceRoleBySquare, PieceType, PlayerSide, TeamMemberRole


_CHESS_LIB_PIECE_TYPE_TO_PIECE_TYPE_MAPPING: dict[int, "PieceType"] = {
    chess.PAWN: "p",
    chess.KNIGHT: "n",
    chess.BISHOP: "b",
    chess.ROOK: "r",
    chess.QUEEN: "q",
    chess.KING: "k",
}


def create_new_daily_challenge(
    *,
    id_: str,
    fen: "FEN",
    bot_first_move: str,
    save: bool,
    fen_before_bot_first_move: "FEN | None" = None,
    default_faction_w: "Faction" = "humans",
    default_faction_b: "Faction" = "undeads",
    bot_side: "PlayerSide" = "b",
    # TODO: allow partial customisation of team members?
    # custom_team_members: "GameTeams | None" = None,
) -> DailyChallenge:
    chess_board = chess.Board(fen)

    if fen_before_bot_first_move is None:
        fen_before_bot_first_move = calculate_fen_before_bot_first_move(
            chess_board=chess_board, bot_first_move=bot_first_move, bot_side=bot_side
        )

    team_members_counters: dict["PlayerSide", dict["PieceType", list[int]]] = {
        # first int of the tuple is the current counter, second int is the maximum value for that counter
        # 9 queens on a player's side is quite an extreme case, but it's theoretically possible via pawn promotions ^^
        "w": {"p": [1, 8], "n": [1, 2], "b": [1, 2], "r": [1, 2], "q": [0, 9], "k": [0, 1]},
        "b": {"p": [1, 8], "n": [1, 2], "b": [1, 2], "r": [1, 2], "q": [0, 9], "k": [0, 1]},
    }

    piece_role_by_square: "PieceRoleBySquare" = {}

    piece_faction: dict["PlayerSide", "Faction"] = {
        "w": default_faction_w,
        "b": default_faction_b,
    }

    teams: "GameTeams" = {"w": [], "b": []}

    for chess_square, chess_piece in chess_board.piece_map().items():
        piece_player_side = chess_lib_color_to_player_side(chess_piece.color)
        piece_type = _CHESS_LIB_PIECE_TYPE_TO_PIECE_TYPE_MAPPING[chess_piece.piece_type]
        team_member_role_counter, piece_role_max_value = team_members_counters[piece_player_side][piece_type]
        piece_role = cast(
            "PieceRole", f"{piece_type}{team_member_role_counter}" if team_member_role_counter > 0 else piece_type
        )
        team_member_role = cast("TeamMemberRole", piece_role.upper() if piece_player_side == "w" else piece_role)

        piece_role_counter_new = team_member_role_counter + 1
        if piece_role_counter_new > piece_role_max_value:
            raise ValueError(
                f"Cannot create more than {piece_role_max_value} pieces(s) in a game for type '{piece_type}'"
            )
        team_members_counters[piece_player_side][piece_type][0] = piece_role_counter_new

        square = square_from_int(chess_square)
        piece_role_by_square[square] = team_member_role

        team_member: "TeamMember" = {
            "role": team_member_role,
            "faction": piece_faction[piece_player_side],
        }
        teams[piece_player_side].append(team_member)

    # Give a name to the player's team members
    _set_character_names_for_non_bot_side(teams, bot_side=bot_side)

    challenge = DailyChallenge(
        id=id_,
        fen=fen,
        fen_before_bot_first_move=fen_before_bot_first_move,
        piece_role_by_square=piece_role_by_square,
        teams=teams,
        bot_first_move=bot_first_move,
    )

    if save:
        challenge.save()

    return challenge


def _set_character_names_for_non_bot_side(teams: "GameTeams", bot_side: "PlayerSide") -> None:
    player_side: "PlayerSide" = "w" if bot_side == "b" else "b"
    player_team_members = teams[player_side]
    first_names = random.sample(FIRST_NAMES, k=len(player_team_members))
    last_names = random.sample(LAST_NAMES, k=len(player_team_members))
    for team_member in player_team_members:
        team_member["first_name"] = first_names.pop()
        team_member["last_name"] = last_names.pop()