from typing import TYPE_CHECKING

from django.core.exceptions import SuspiciousOperation

from ..chess_logic import do_chess_move
from ..helpers import get_active_player_side_from_fen

if TYPE_CHECKING:
    from ..daily_challenge import PlayerGameState
    from ..types import Square


def move_daily_challenge_piece(
    *,
    game_state: "PlayerGameState",
    from_: "Square",
    to: "Square",
) -> "PlayerGameState":
    fen = game_state["fen"]
    active_player_side = get_active_player_side_from_fen(fen)
    try:
        move_result = do_chess_move(
            fen=fen,
            from_=from_,
            to=to,
        )
    except ValueError as err:
        raise SuspiciousOperation(f"Suspicious chess move: '{err}'") from err

    team_member_role_by_square = game_state["piece_role_by_square"].copy()
    current_piece_role = team_member_role_by_square[from_]
    if promotion := move_result["promotion"]:
        current_piece_role += promotion.upper() if active_player_side == "w" else promotion  # type: ignore

    for move_from, move_to in move_result["changes"].items():
        if move_to is None:
            continue  # We can just ignore captures there, as the capturing piece just replaces it in the mapping :-)
        team_member_role_by_square[move_to] = team_member_role_by_square[move_from]
        del team_member_role_by_square[move_from]  # this square is now empty

    # Right, let's return the new game state!
    new_game_state: "PlayerGameState" = {
        "fen": move_result["fen"],
        "piece_role_by_square": team_member_role_by_square,
    }

    return new_game_state
