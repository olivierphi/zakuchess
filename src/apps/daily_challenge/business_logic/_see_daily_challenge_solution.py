import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState


def see_daily_challenge_solution(
    *,
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
) -> "PlayerGameState":
    # This field is always set on a published challenge - let's make the
    # type checker happy:
    assert challenge.piece_role_by_square

    new_game_state = copy.copy(game_state)  # msgspec Structs implement `__copy__`
    new_game_state.see_solution = True
    new_game_state.current_attempt_turns_counter = 0
    new_game_state.fen = challenge.fen
    new_game_state.piece_role_by_square = challenge.piece_role_by_square
    new_game_state.moves = ""

    # Server stats
    # TODO: server starts for seeing the solution
    # if not is_preview:
    #     DailyChallengeStats.objects.increment_today_restarts_count()

    return new_game_state
