import functools
from typing import TYPE_CHECKING

from django.core.exceptions import BadRequest

from apps.chess.types import ChessLogicException

from ..utils.views_helpers import htmx_aware_redirect
from .cookie_helpers import clear_daily_challenge_game_state_in_session
from .view_helpers import GameContext

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from .models import PlayerStats


def handle_chess_logic_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChessLogicException as exc:
            raise BadRequest(str(exc)) from exc

    return wrapper


def with_game_context(func):
    @functools.wraps(func)
    def wrapper(request: "HttpRequest", *args, **kwargs):
        ctx = GameContext.create_from_request(request)
        return func(request, *args, ctx=ctx, **kwargs)

    return wrapper


def redirect_if_game_not_started(func):
    @functools.wraps(func)
    def wrapper(request: "HttpRequest", *args, ctx: GameContext, **kwargs):
        if ctx.created:
            return _redirect_to_game_view_screen_with_brand_new_game(request, ctx.stats)
        return func(request, *args, ctx=ctx, **kwargs)

    return wrapper


def _redirect_to_game_view_screen_with_brand_new_game(
    request: "HttpRequest", player_stats: "PlayerStats"
) -> "HttpResponse":
    clear_daily_challenge_game_state_in_session(
        request=request, player_stats=player_stats
    )

    return htmx_aware_redirect(request, "daily_challenge:daily_game_view")
