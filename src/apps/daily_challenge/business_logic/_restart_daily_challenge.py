import copy
from typing import TYPE_CHECKING

from ..models import DailyChallengeStats

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState


def restart_daily_challenge(
    *,
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    is_preview: bool = False,
) -> "PlayerGameState":
    # These fields are always set on a published challenge - let's make the
    # type checker happy:
    assert (
        challenge.fen_before_bot_first_move
        and challenge.piece_role_by_square_before_bot_first_move
    )

    new_game_state = copy.copy(game_state)  # msgspec Structs implement `__copy__`
    new_game_state.attempts_counter += 1
    new_game_state.current_attempt_turns_counter = 0
    # Restarting the daily challenge costs one move:
    new_game_state.turns_counter += 1
    # Back to the initial state:
    new_game_state.fen = challenge.fen_before_bot_first_move
    new_game_state.piece_role_by_square = (
        challenge.piece_role_by_square_before_bot_first_move
    )
    new_game_state.moves = ""

    # Server stats
    if not is_preview:
        DailyChallengeStats.objects.increment_today_restarts_count()

    return new_game_state
