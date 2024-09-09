import logging
import textwrap
from typing import TYPE_CHECKING

from apps.chess.chess_helpers import uci_move_squares

from ..models import DailyChallengeStats
from ._move_daily_challenge_piece import move_daily_challenge_piece

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState


_logger = logging.getLogger("apps.daily_challenge")

_MOVES_STR_MIN_LENGTH = (
    4 + 8  # 4 chars for the bot's 1st move, plus 8 chars for the 1st turn's 2 moves
)


def undo_last_move(
    *,
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    is_staff_user: bool = False,
) -> "PlayerGameState":
    # A published challenge always has a `piece_role_by_square`:
    assert challenge.piece_role_by_square

    moves = game_state.moves
    if len(moves) < _MOVES_STR_MIN_LENGTH:
        _logger.warning(
            "Trying to undo the last move, but there are not enough moves to undo?"
        )
        return game_state

    # We could undo the last 2 moves by "unstacking" the "moves" field, but by
    # un-applying moves like this with our `calculate_fen_before_move` function we would
    # lose track of the captures that were made during these moves.
    # --> So instead we restart from the beginning, and replay all the moves except
    # the last 2 ones.

    # Back to the initial state:
    game_state.fen = challenge.fen
    game_state.piece_role_by_square = challenge.piece_role_by_square
    game_state.current_attempt_turns_counter = 0
    game_state.moves = moves[:4]  # we only keep the bot's 1st move there

    # And now, let's replay all the moves!
    # We create a list of UCI moves, without the last 2 ones (which take 8 chars) and
    # without the bot's 1st move (which takes the 1st 4 chars):
    moves_list: list[str] = textwrap.wrap(moves[4:-8], width=4)

    is_my_side = True  # The human player always starts
    # Right, let's replay all the moves from that list now!
    for move_uci in moves_list:
        from_, to = uci_move_squares(move_uci)
        # We cannot simply play each move using the `chess` library, because we need to
        # keep track of the pieces updates in the `piece_role_by_square` field - which
        # can be cumbersome in the case of castling, en passant, or promotion.
        # So let's use our own `move_daily_challenge_piece` function instead:
        game_state, _ = move_daily_challenge_piece(
            game_state=game_state, from_=from_, to=to, is_my_side=is_my_side
        )
        is_my_side = not is_my_side

    # Undoing the last move can only be done once per challenge:
    game_state.undo_used = True

    # Server stats
    if not is_staff_user:
        DailyChallengeStats.objects.increment_today_undos_count()

    return game_state
