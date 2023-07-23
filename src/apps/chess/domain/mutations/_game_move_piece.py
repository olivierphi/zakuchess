from typing import TYPE_CHECKING

from django.core.exceptions import SuspiciousOperation

from apps.chess.domain.helpers import player_side_other

from ...models import Game
from ..chess_logic import do_chess_move
from ..dto import ChessMoveResult

if TYPE_CHECKING:
    from ..types import Square


def game_move_piece(*, game: Game, from_: "Square", to: "Square") -> ChessMoveResult:
    print(f"game_move_piece(); start. {game.active_player=}")
    try:
        move_result = do_chess_move(
            fen=game.fen,
            player_side=game.active_player,
            from_=from_,
            to=to,
        )
    except ValueError as err:
        raise SuspiciousOperation(f"Suspicious chess move: '{err}'") from err

    team_member_role_by_square = game.piece_role_by_square
    current_piece_role = team_member_role_by_square[from_]
    if promotion := move_result["promotion"]:
        current_piece_role += promotion.upper() if game.active_player == "w" else promotion  # type: ignore

    for move_from, move_to in move_result["changes"].items():
        if move_to is None:
            continue  # We can just ignore captures there, as the capturing piece just replaces it in the mapping :-)
        del team_member_role_by_square[move_from]
        team_member_role_by_square[move_to] = current_piece_role

    # Right, let's update that model!
    game.fen = move_result["fen"]
    game.active_player = player_side_other(game.active_player)
    game.piece_role_by_square = team_member_role_by_square
    game.save(update_fields=("fen", "active_player", "piece_role_by_square", "updated_at"))

    print(f"game_move_piece(); end. {game.active_player=}")

    return move_result
