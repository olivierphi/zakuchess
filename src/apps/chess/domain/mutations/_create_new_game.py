from typing import TYPE_CHECKING, cast

import chess

from ...models import Game, Team, TeamMember
from ..consts import PLAYER_SIDES, SQUARES
from ..helpers import (
    get_active_player_from_chess_board,
    player_side_from_piece_role,
    square_from_int,
    team_member_role_from_piece_role,
)
from ..queries import generate_team_members

if TYPE_CHECKING:
    from ..types import FEN, PieceRoleBySquare, PieceSymbol, PlayerSide, TeamMemberRole

# Useful for quick tests:
# Good resource to create such FENs: https://www.dailychess.com/chess/chess-fen-viewer.php
_FEN_WHITE_ABOUT_TO_PROMOTE = "kn6/6P1/8/8/8/8/8/KN6 w - - 0 1"
# _FEN_WHITE_ABOUT_TO_PROMOTE = "rn1qkbnr/p1P2ppp/b2p4/1p2p3/8/1P6/P1P1PPPP/RNBQKBNR w KQkq - 0 6"
_FEN_WHITE_ABOUT_TO_EN_PASSANT = "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
_FEN_BLACK_ABOUT_TO_MOVE_KING = "r1b1kb1r/ppp1qppp/2np1n2/3P4/8/2N1BN2/PPP2PPP/R2QKB1R w KQkq - 2 7"

_STARTING_BOARD = chess.Board()


def create_new_game(
    *,
    fen: "FEN | None" = None,
    bot_side: "PlayerSide | None",
    piece_role_by_square: "PieceRoleBySquare | None" = None,
) -> Game:
    blank_one = fen is None
    chess_board = _STARTING_BOARD if blank_one else chess.Board(fen=fen)

    fen = chess_board.fen()
    active_player = get_active_player_from_chess_board(chess_board)

    if piece_role_by_square is None:
        piece_role_by_square = _get_initial_piece_roles_by_square(chess_board)

    piece_role_by_square = _sort_piece_role_by_square(piece_role_by_square)

    game = Game.objects.create(
        fen=fen,
        active_player=active_player,
        piece_role_by_square=piece_role_by_square,
        bot_side=bot_side,
    )

    team_member_roles = _get_initial_team_member_roles(piece_role_by_square)
    for player_side in PLAYER_SIDES:
        # We' just state that by convention the first Team is the "w" side,
        # while the second Team is the "b" side:
        roles = team_member_roles[player_side]
        team = Team.objects.create(game=game)
        generate_names: bool = player_side != bot_side
        team_members = []
        for team_member in generate_team_members(roles=roles, generate_names=generate_names):
            team_member.team = team
            team_members.append(team_member)
        TeamMember.objects.bulk_create(team_members)

    return game


def _sort_piece_role_by_square(piece_role_by_square: "PieceRoleBySquare") -> "PieceRoleBySquare":
    sorted_dict: "PieceRoleBySquare" = {}
    for sorted_square in SQUARES:
        if sorted_square in piece_role_by_square:
            sorted_dict[sorted_square] = piece_role_by_square[sorted_square]
    return sorted_dict


def _get_initial_piece_roles_by_square(chess_board: chess.Board) -> "PieceRoleBySquare":
    team_members_counters: dict["PieceSymbol", int] = {
        # fmt: off
        "P": 1, "N": 1, "B": 1, "R": 1,
        "p": 1, "n": 1, "b": 1, "r": 1,
        # fmt: on
    }

    result: "PieceRoleBySquare" = {}
    for square_int, piece in chess_board.piece_map().items():
        square = square_from_int(square_int)
        piece_symbol = cast("PieceSymbol", piece.symbol())
        piece_counter: int | None = team_members_counters.get(piece_symbol)
        role = cast("TeamMemberRole", f"{piece_symbol}{piece_counter if piece_counter else ''}")
        result[square] = role
        if piece_counter:
            team_members_counters[piece_symbol] += 1

    return result


def _get_initial_team_member_roles(
    piece_role_by_square: "PieceRoleBySquare",
) -> "dict[PlayerSide, list[TeamMemberRole]]":
    result: "dict[PlayerSide, list[TeamMemberRole]]" = {"w": [], "b": []}
    for piece_role in piece_role_by_square.values():
        player_side = player_side_from_piece_role(piece_role)
        team_member_role = team_member_role_from_piece_role(piece_role)
        result[player_side].append(team_member_role)
    return result
