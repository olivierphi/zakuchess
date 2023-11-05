from typing import TYPE_CHECKING

from django.utils.timezone import now

from .models import DailyChallenge
from .types import PlayerGameState, PlayerSessionContent

if TYPE_CHECKING:
    from django.http import HttpRequest

_PLAYER_CONTENT_SESSION_KEY = "pc"


def get_or_create_daily_challenge_state_for_player(
    *, request: "HttpRequest", challenge: DailyChallenge
) -> tuple[PlayerGameState, bool]:
    """
    Returns the game state for the given challenge, creating it if it doesn't exist yet.
    The second value is a boolean indicating if the game state was created or not.
    """
    # A published challenge always has a `piece_role_by_square` non-null field:
    assert challenge.piece_role_by_square

    player_cookie_content = get_player_session_content(request)
    challenge_id = today_daily_challenge_id(request)
    game_state: PlayerGameState | None = player_cookie_content["games"].get(
        challenge_id
    )

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
        )
        created = True
    else:
        created = False

    return game_state, created


def get_player_session_content(request: "HttpRequest") -> PlayerSessionContent:
    player_cookie_content: PlayerSessionContent | None = request.session.get(
        _PLAYER_CONTENT_SESSION_KEY
    )
    if player_cookie_content is None:
        return PlayerSessionContent(games={})
    return player_cookie_content


def save_daily_challenge_state_in_session(
    *, request: "HttpRequest", game_state: PlayerGameState
) -> None:
    # Erases other games data!
    challenge_id = today_daily_challenge_id(request)
    request.session[_PLAYER_CONTENT_SESSION_KEY] = {"games": {challenge_id: game_state}}


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
