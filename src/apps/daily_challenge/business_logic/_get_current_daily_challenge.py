import logging
from typing import TYPE_CHECKING

from django.utils import timezone

from ..models import DailyChallengeStatus

if TYPE_CHECKING:
    from ..models import DailyChallenge

_logger = logging.getLogger("apps.daily_challenge")


def get_current_daily_challenge() -> "DailyChallenge":
    from ..models import DailyChallenge

    today = timezone.now().date()
    today_as_strings = (
        # We may have a challenge for this specific day of this specific year:
        today.strftime("%Y-%m-%d"),
        # If not, we'll look for a challenge for this specific day of any year:
        today.strftime("%m-%d"),
    )

    for today_str in today_as_strings:
        # N.B. On a non-SQLite database we would have tried to use a single query
        # to fetch both cases, but n+1 queries are not a problem with SQlite.
        try:
            return DailyChallenge.objects.get(
                status=DailyChallengeStatus.PUBLISHED,
                lookup_key=today_str,
            )
        except DailyChallenge.DoesNotExist:
            pass

    # TODO: implement multiple fallback daily challenges (and use a modulo to select 1)
    _logger.info("No published daily challenge found, using the fallback one.")
    return DailyChallenge.objects.get(lookup_key="fallback")
