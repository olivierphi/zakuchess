from typing import TYPE_CHECKING

from django.utils.timezone import now

if TYPE_CHECKING:
    from ..types import PlayerStats


def manage_new_daily_challenge_logic(stats: "PlayerStats") -> None:
    """
    When a player starts a new daily challenge, we need to update part of their stats.
    """

    # One more game played for this player!
    stats.games_count += 1

    # Do we increment the current streak, or restart it from the beginning?
    today = now().date()
    is_on_a_streak: bool = False
    if stats.last_played:
        if (today - stats.last_played).days == 1:
            is_on_a_streak = True
    if is_on_a_streak:
        stats.current_streak += 1
    else:
        stats.current_streak = 1

    # Max streak management:
    if stats.current_streak > stats.max_streak:
        stats.max_streak = stats.current_streak

    # Last played date:
    stats.last_played = today
