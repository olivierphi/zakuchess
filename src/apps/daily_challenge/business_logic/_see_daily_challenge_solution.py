import copy
from typing import TYPE_CHECKING

from ..models import DailyChallengeStats
from ._has_player_won_today import has_player_won_today

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState, PlayerStats


def see_daily_challenge_solution(
    *,
    challenge: "DailyChallenge",
    stats: "PlayerStats",
    game_state: "PlayerGameState",
    is_staff_user: bool = False,
) -> "PlayerGameState":
    # This field is always set on a published challenge - let's make the
    # type checker happy:
    assert challenge.piece_role_by_square

    new_game_state = copy.copy(game_state)  # msgspec Structs implement `__copy__`
    new_game_state.solution_index = 0
    new_game_state.current_attempt_turns_counter = 0
    new_game_state.fen = challenge.fen
    new_game_state.piece_role_by_square = challenge.piece_role_by_square
    new_game_state.moves = ""

    # If we're seeing the solution without having won today first,
    # that's the end of our current streak 😔
    # TODO: write a test for this! It's a bit late right now so I'm rushing it 😓
    if not has_player_won_today(stats):
        stats.current_streak = 0

    # Server stats
    if not is_staff_user:
        DailyChallengeStats.objects.increment_today_see_solution_count()

    return new_game_state
