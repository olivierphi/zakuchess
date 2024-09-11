from typing import TYPE_CHECKING, NamedTuple

from apps.chess.business_logic import do_chess_move_with_piece_role_by_square

from ..models import PlayerGameOverState

if TYPE_CHECKING:
    from apps.chess.types import PieceRole, Square

    from ..models import PlayerGameState


class MoveDailyChallengePieceResult(NamedTuple):
    game_state: "PlayerGameState"
    captured_piece: "PieceRole | None"


def move_daily_challenge_piece(
    *,
    game_state: "PlayerGameState",
    from_: "Square",
    to: "Square",
    is_my_side: bool,
) -> MoveDailyChallengePieceResult:
    move_result, piece_role_by_square, captured_piece = (
        do_chess_move_with_piece_role_by_square(
            fen=game_state.fen,
            from_=from_,
            to=to,
            piece_role_by_square=game_state.piece_role_by_square,
        )
    )

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

    return MoveDailyChallengePieceResult(new_game_state, captured_piece)
