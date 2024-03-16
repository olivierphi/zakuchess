from typing import TYPE_CHECKING

from django.utils.timezone import now

from ..models import DailyChallengeStats, PlayerGameOverState

if TYPE_CHECKING:
    from ..models import PlayerGameState, PlayerStats


def manage_daily_challenge_moved_piece_logic(
    *,
    game_state: "PlayerGameState",
    stats: "PlayerStats",
    is_preview: bool = False,
    is_staff_user: bool = False,
) -> None:
    """
    When a player moves a piece during new daily challenge,
    we may need to update part of their stats.
    """

    assert game_state.game_over == PlayerGameOverState.PLAYING

    if is_preview:
        return None

    is_1st_turn_of_1st_attempt = (
        game_state.attempts_counter == 0
        and game_state.current_attempt_turns_counter == 1
    )
    if is_1st_turn_of_1st_attempt:
        # One more game played for this player!
        stats.games_count += 1
        # Last played date:
        stats.last_played = now().date()

    # Server stats
    if not is_staff_user:
        if is_1st_turn_of_1st_attempt:
            DailyChallengeStats.objects.increment_today_played_count()
        is_2nd_turn_of_1st_attempt = (
            game_state.attempts_counter == 0
            and game_state.current_attempt_turns_counter == 2
        )
        if is_2nd_turn_of_1st_attempt:
            DailyChallengeStats.objects.increment_played_challenges_count()
        DailyChallengeStats.objects.increment_today_turns_count()
