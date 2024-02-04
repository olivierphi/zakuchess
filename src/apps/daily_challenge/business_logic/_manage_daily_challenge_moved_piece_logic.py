from typing import TYPE_CHECKING

from django.utils.timezone import now

from ..models import DailyChallengeStats, PlayerGameOverState

if TYPE_CHECKING:
    from ..models import PlayerGameState, PlayerStats


def manage_daily_challenge_moved_piece_logic(
    *, game_state: "PlayerGameState", stats: "PlayerStats"
) -> None:
    """
    When a player moves a piece during new daily challenge,
    we may need to update part of their stats.
    """

    assert game_state.game_over == PlayerGameOverState.PLAYING

    if game_state.current_attempt_turns_counter == 1:
        # One more game played for this player!
        stats.games_count += 1
        # Last played date:
        stats.last_played = now().date()
        # Server stats
        DailyChallengeStats.objects.increment_today_played_count()

    # Server stats
    DailyChallengeStats.objects.increment_today_turns_count()
