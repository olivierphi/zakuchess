from typing import TYPE_CHECKING

from django.utils.timezone import now

if TYPE_CHECKING:
    from ..types import PlayerStats


def player_won_yesterday(stats: "PlayerStats") -> bool:
    today = now().date()
    return bool((last_won := stats.last_won) and (today - last_won).days == 1)
