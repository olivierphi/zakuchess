import logging
import time
from typing import TYPE_CHECKING, NamedTuple

import chess

from ...chess.business_logic import do_chess_move_with_piece_role_by_square
from ...chess.chess_helpers import uci_move_squares

if TYPE_CHECKING:
    from collections.abc import Sequence

    import chess.pgn

    from apps.chess.types import PieceRoleBySquare, UCIMove

    from ...chess.models import GameFactions, GameTeams

_logger = logging.getLogger(__name__)


class RebuildGameFromMovesResult(NamedTuple):
    chess_board: chess.Board
    teams: "GameTeams"
    piece_role_by_square: "PieceRoleBySquare"
    moves: "Sequence[UCIMove]"


def rebuild_game_from_moves(
    *, uci_moves: "Sequence[UCIMove]", factions: "GameFactions"
) -> RebuildGameFromMovesResult:
    from ._create_teams_and_piece_role_by_square_for_starting_position import (
        create_teams_and_piece_role_by_square_for_starting_position,
    )

    start_time = time.monotonic()

    # We start with a "starting position "chess board"...
    teams, piece_role_by_square_tuple = (
        create_teams_and_piece_role_by_square_for_starting_position(factions)
    )
    piece_role_by_square = dict(piece_role_by_square_tuple)

    # ...and then we apply the moves from the game data to it, one by one:
    # (while keeping track of the piece roles on the board, so if "p1" moves,
    # we can "follow" that pawn)
    chess_board = chess.Board()
    for move in uci_moves:
        from_, to = uci_move_squares(move)
        move_result, piece_role_by_square, captured_piece = (
            do_chess_move_with_piece_role_by_square(
                from_=from_,
                to=to,
                piece_role_by_square=piece_role_by_square,
                chess_board=chess_board,
            )
        )

    _logger.info(
        "`rebuild_game_from_moves` took %d ms. for %d moves",
        (time.monotonic() - start_time) * 1000,
        len(uci_moves),
    )

    return RebuildGameFromMovesResult(
        chess_board=chess_board,
        teams=teams,
        piece_role_by_square=piece_role_by_square,
        moves=uci_moves,
    )
