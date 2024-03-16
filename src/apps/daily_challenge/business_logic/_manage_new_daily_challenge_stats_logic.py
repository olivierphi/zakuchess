from typing import TYPE_CHECKING

from ..models import DailyChallengeStats
from ._has_player_won_yesterday import has_player_won_yesterday

if TYPE_CHECKING:
    from ..models import PlayerStats


def manage_new_daily_challenge_stats_logic(
    stats: "PlayerStats", *, is_preview: bool = False, is_staff_user: bool = False
) -> None:
    """
    When a player starts a new daily challenge,
    we may need to update part of their stats.
    """

    if is_preview:
        return None

    # Do we restart the current streak from the beginning?
    if not has_player_won_yesterday(stats):
        stats.current_streak = 0  # back to a brand-new streak flow

    # Server stats
    if not is_staff_user:
        DailyChallengeStats.objects.increment_today_created_count()

    # We could increment the `games_count` counter of the stats here,
    # but let's do it only when the player moves a piece at least - so we'll do
    # that in `_manage_daily_challenge_moved_piece_logic` instead.
