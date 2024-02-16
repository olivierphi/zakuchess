from typing import TYPE_CHECKING, cast

from apps.chess.business_logic import do_chess_move
from apps.chess.helpers import get_active_player_side_from_fen
from apps.chess.types import ChessInvalidStateException

from ..models import PlayerGameOverState, PlayerGameState

if TYPE_CHECKING:
    from apps.chess.types import PieceRole, PieceSymbol, Square


def move_daily_challenge_piece(
    *,
    game_state: "PlayerGameState",
    from_: "Square",
    to: "Square",
    is_my_side: bool,
) -> tuple["PlayerGameState", "PieceRole | None"]:
    fen = game_state.fen
    active_player_side = get_active_player_side_from_fen(fen)
    try:
        move_result = do_chess_move(
            fen=fen,
            from_=from_,
            to=to,
        )
    except ValueError as err:
        raise ChessInvalidStateException(f"Suspicious chess move: '{err}'") from err

    piece_role_by_square = game_state.piece_role_by_square.copy()
    if promotion := move_result["promotion"]:
        # Let's promote that piece!
        piece_promotion = cast(
            "PieceSymbol", promotion.upper() if active_player_side == "w" else promotion
        )
        piece_role_by_square[from_] += piece_promotion  # type: ignore

    captured_piece: "PieceRole | None" = None
    if move_result["is_capture"]:
        captured_piece = game_state.piece_role_by_square[to]

    for move_from, move_to in move_result["changes"].items():
        if move_to is None:
            # We can just ignore captures there, as the capturing piece
            # just replaces it in the mapping :-)
            continue
        piece_role_by_square[move_to] = piece_role_by_square[move_from]
        del piece_role_by_square[move_from]  # this square is now empty

    if game_over := move_result["game_over"]:
        game_over_state = (
            PlayerGameOverState.WON
            if game_over["winner"] == "w"
            else PlayerGameOverState.LOST
        )
    else:
        game_over_state = PlayerGameOverState.PLAYING

    # Right, let's return the new game state!
    new_game_state = game_state.replace(
        fen=move_result["fen"],
        piece_role_by_square=piece_role_by_square,
        moves=f"{game_state.moves}{from_}{to}",
        game_over=game_over_state,
    )

    if is_my_side:
        new_game_state.turns_counter += 1
        new_game_state.current_attempt_turns_counter += 1

    return new_game_state, captured_piece
