import dataclasses
from typing import TYPE_CHECKING, cast

from .business_logic import manage_new_daily_challenge_stats_logic
from .cookie_helpers import (
    get_or_create_daily_challenge_state_for_player,
    get_user_prefs_from_request,
)
from .models import DailyChallengeStats

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.models import UserPrefs

    from .models import DailyChallenge, PlayerGameState, PlayerStats


@dataclasses.dataclass(eq=False, kw_only=True, frozen=True, slots=True)
class GameContext:
    """
    A context object that holds the current daily challenge, the current game state,
    and some other data that is useful for our Views (aka "Controllers" in MVC).
    """

    challenge: "DailyChallenge"

    is_preview: bool
    is_staff_user: bool
    """`is_preview` is True if we're in admin preview mode"""
    game_state: "PlayerGameState"
    stats: "PlayerStats"
    user_prefs: "UserPrefs"
    created: bool
    """if the game state was created on the fly as we were initialising that object"""
    board_id: str = "main"

    @classmethod
    def create_from_request(cls, request: "HttpRequest") -> "GameContext":
        is_staff_user: bool = request.user.is_staff
        challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
        game_state, stats, created, is_returning_player = (
            get_or_create_daily_challenge_state_for_player(
                request=request, challenge=challenge
            )
        )
        user_prefs = get_user_prefs_from_request(request)
        # TODO: validate the "board_id" data?
        board_id = cast(str, request.GET.get("board_id", "main"))

        if created:
            manage_new_daily_challenge_stats_logic(
                stats, is_preview=is_preview, is_staff_user=is_preview
            )

        if is_returning_player and not is_staff_user:
            # The player (not staff) has played a previous challenge, but not today.
            # Let's take note of this while we're there :-)
            DailyChallengeStats.objects.increment_today_returning_players_count()

        return cls(
            challenge=challenge,
            is_preview=is_preview,
            is_staff_user=is_staff_user,
            game_state=game_state,
            stats=stats,
            user_prefs=user_prefs,
            created=created,
            board_id=board_id,
        )


def get_current_daily_challenge_or_admin_preview(
    request: "HttpRequest",
) -> tuple["DailyChallenge", bool]:
    from .business_logic import get_current_daily_challenge
    from .models import DailyChallenge

    if request.user.is_staff:
        admin_daily_challenge_lookup_key = request.get_signed_cookie(
            "admin_daily_challenge_lookup_key", default=None
        )
        if admin_daily_challenge_lookup_key:
            return (
                DailyChallenge.objects.get(lookup_key=admin_daily_challenge_lookup_key),
                True,
            )

    return get_current_daily_challenge(), False
