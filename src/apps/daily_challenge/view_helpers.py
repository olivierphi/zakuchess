import dataclasses
from typing import TYPE_CHECKING, cast

from .business_logic import manage_new_daily_challenge_stats_logic
from .cookie_helpers import get_or_create_daily_challenge_state_for_player

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .models import DailyChallenge, PlayerGameState, PlayerStats


@dataclasses.dataclass(frozen=True)
class GameContext:
    challenge: "DailyChallenge"

    is_preview: bool
    """if we're in admin preview mode"""
    game_state: "PlayerGameState"
    stats: "PlayerStats"
    created: bool
    """if the game state was created on the fly as we were initialising that object"""
    board_id: str = "main"

    @classmethod
    def create_from_request(cls, request: "HttpRequest") -> "GameContext":
        challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
        game_state, stats, created = get_or_create_daily_challenge_state_for_player(
            request=request, challenge=challenge
        )
        # TODO: validate the "board_id" data
        board_id = cast(str, request.GET.get("board_id", "main"))

        if created:
            manage_new_daily_challenge_stats_logic(stats)

        return cls(
            challenge=challenge,
            is_preview=is_preview,
            game_state=game_state,
            stats=stats,
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
