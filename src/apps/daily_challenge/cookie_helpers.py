import logging
from typing import TYPE_CHECKING

import msgspec
from django.utils.timezone import now

from .models import DailyChallenge
from .types import PlayerGameState, PlayerSessionContent, PlayerStats

if TYPE_CHECKING:
    from django.http import HttpRequest

_PLAYER_CONTENT_SESSION_KEY = "pc"

_logger = logging.getLogger(__name__)


def get_or_create_daily_challenge_state_for_player(
    *, request: "HttpRequest", challenge: DailyChallenge
) -> tuple[PlayerGameState, PlayerStats, bool]:
    """
    Returns the game state for the given challenge, creating it if it doesn't exist yet.
    The second value is a boolean indicating if the game state was created or not.
    """
    # A published challenge always has a `piece_role_by_square` non-null field:
    assert challenge.piece_role_by_square

    player_cookie_content = get_player_session_content(request)
    # TODO: remove this assertion once all cookies have been migrated
    assert player_cookie_content.stats

    challenge_id = today_daily_challenge_id(request)
    game_state: PlayerGameState | None = player_cookie_content.games.get(challenge_id)

    if game_state is None:
        game_state = PlayerGameState(
            attempts_counter=0,
            turns_counter=0,
            current_attempt_turns_counter=0,
            fen=challenge.fen,
            piece_role_by_square=challenge.piece_role_by_square,
            moves="",
        )
        save_daily_challenge_state_in_session(
            request=request,
            game_state=game_state,
            player_stats=player_cookie_content.stats,
        )
        created = True
    else:
        created = False

    return game_state, player_cookie_content.stats, created


def get_player_session_content(request: "HttpRequest") -> PlayerSessionContent:
    def new_content():
        return PlayerSessionContent(games={}, stats=PlayerStats())

    cookie_content: str | None = request.session.get(_PLAYER_CONTENT_SESSION_KEY)
    if cookie_content is None or len(cookie_content) < 10:
        return new_content()

    try:
        session_content = msgspec.json.decode(
            cookie_content.encode(), type=PlayerSessionContent
        )
        if not session_content.stats:
            # TODO: remove this condition once all cookies have been migrated
            session_content.stats = PlayerStats()
        return session_content
    except msgspec.MsgspecError:
        _logger.exception(
            "Could not decode cookie content; restarting with a blank one."
        )
        return new_content()


def save_daily_challenge_state_in_session(
    *, request: "HttpRequest", game_state: PlayerGameState, player_stats: PlayerStats
) -> None:
    # Erases other games data!
    challenge_id = today_daily_challenge_id(request)
    session_content = PlayerSessionContent(
        games={challenge_id: game_state}, stats=player_stats
    )
    cookie_content: str = msgspec.json.encode(session_content).decode()
    request.session[_PLAYER_CONTENT_SESSION_KEY] = cookie_content


def clear_daily_challenge_state_in_session(*, request: "HttpRequest") -> None:
    # Erases all games data!
    request.session[_PLAYER_CONTENT_SESSION_KEY] = {"games": {}}


def today_daily_challenge_id(request: "HttpRequest") -> str:
    if request.user.is_staff:
        admin_daily_challenge_lookup_key = request.get_signed_cookie(
            "admin_daily_challenge_lookup_key", default=None
        )
        if admin_daily_challenge_lookup_key:
            return f"admin-preview-{admin_daily_challenge_lookup_key}"
    return now().date().isoformat()
