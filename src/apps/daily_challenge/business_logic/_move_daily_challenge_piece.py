from typing import TYPE_CHECKING, cast

from django.core.exceptions import SuspiciousOperation

from apps.chess.chess_logic import do_chess_move
from apps.chess.helpers import get_active_player_side_from_fen

if TYPE_CHECKING:
    from apps.chess.types import PieceSymbol, Square

    from ..types import PlayerGameState


def move_daily_challenge_piece(
    *,
    game_state: "PlayerGameState",
    from_: "Square",
    to: "Square",
    is_my_side: bool,
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

    piece_role_by_square = game_state["piece_role_by_square"].copy()
    if promotion := move_result["promotion"]:
        # Let's promote that piece!
        piece_promotion = cast(
            "PieceSymbol", promotion.upper() if active_player_side == "w" else promotion
        )
        piece_role_by_square[from_] += piece_promotion  # type: ignore

    for move_from, move_to in move_result["changes"].items():
        if move_to is None:
            # We can just ignore captures there, as the capturing piece
            # just replaces it in the mapping :-)
            continue
        piece_role_by_square[move_to] = piece_role_by_square[move_from]
        del piece_role_by_square[move_from]  # this square is now empty

    # Right, let's return the new game state!
    new_game_state: "PlayerGameState" = {
        # We keep these as-is...
        "turns_counter": game_state["turns_counter"],
        "attempts_counter": game_state["attempts_counter"],
        "current_attempt_turns_counter": game_state["current_attempt_turns_counter"],
        # ...but update those:
        "fen": move_result["fen"],
        "piece_role_by_square": piece_role_by_square,
    }

    if is_my_side:
        new_game_state["turns_counter"] += 1
        new_game_state["current_attempt_turns_counter"] += 1

    return new_game_state
