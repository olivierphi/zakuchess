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

    is_1st_attempt = game_state.attempts_counter == 0
    is_1st_turn = game_state.current_attempt_turns_counter == 1
    is_1st_turn_of_1st_attempt = is_1st_attempt and is_1st_turn
    if is_1st_turn_of_1st_attempt:
        # One more game played for this player!
        stats.games_count += 1
        # Last played date:
        stats.last_played = now().date()

    if is_staff_user:
        # Server stats are only updated for non-staff users
        return

    DailyChallengeStats.objects.increment_today_turns_count()

    if is_1st_turn:
        # Here we count all 1st turns, whatever attempt:
        DailyChallengeStats.objects.increment_today_attempts_count()

    is_2nd_turn_of_1st_attempt = (
        is_1st_attempt and game_state.current_attempt_turns_counter == 2
    )
    if is_2nd_turn_of_1st_attempt:
        # ...whereas here we count only 2nd turns of 1st attempts:
        DailyChallengeStats.objects.increment_played_challenges_count()

        if game_state.is_returning_player:
            # The player (not staff) has played a previous challenge, but not today.
            # Let's take note of this while we're there :-)
            DailyChallengeStats.objects.increment_today_returning_players_count()
