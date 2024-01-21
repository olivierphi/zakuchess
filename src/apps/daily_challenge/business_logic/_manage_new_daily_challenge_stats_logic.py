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

    # Last played date:
    stats.last_played = now().date()
