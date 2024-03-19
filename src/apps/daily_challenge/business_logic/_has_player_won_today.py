from typing import TYPE_CHECKING

from django.utils.timezone import now

if TYPE_CHECKING:
    from ..models import PlayerStats


def has_player_won_today(stats: "PlayerStats") -> bool:
    today = now().date()
    return bool((last_won := stats.last_won) and today == last_won)
