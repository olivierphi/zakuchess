from datetime import date
from typing import TYPE_CHECKING

from .business_logic.daily_challenge import PlayerGameState, PlayerSessionContent
from .models import DailyChallenge

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
    player_cookie_content = get_player_session_content(request)
    challenge_id = today_daily_challenge_id()
    game_state: PlayerGameState | None = player_cookie_content["games"].get(challenge_id)

    if game_state is None:
        game_state = PlayerGameState(
            turns_counter=0,
            fen=challenge.fen,
            piece_role_by_square=challenge.piece_role_by_square,
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
    player_cookie_content: PlayerSessionContent | None = request.session.get(_PLAYER_CONTENT_SESSION_KEY)
    if player_cookie_content is None:
        return PlayerSessionContent(games={})
    return player_cookie_content


def save_daily_challenge_state_in_session(*, request: "HttpRequest", game_state: PlayerGameState) -> None:
    # Erases other games data!
    challenge_id = today_daily_challenge_id()
    request.session[_PLAYER_CONTENT_SESSION_KEY] = {"games": {challenge_id: game_state}}


def today_daily_challenge_id() -> str:
    return date.today().isoformat()
