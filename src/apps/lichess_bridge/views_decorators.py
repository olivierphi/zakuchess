import functools
from typing import TYPE_CHECKING

from asgiref.sync import iscoroutinefunction
from django.core.exceptions import BadRequest
from django.shortcuts import redirect

from ..chess.types import ChessLogicException
from ..webui.cookie_helpers import get_user_prefs_from_request
from . import cookie_helpers

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .models import LichessAccessToken


def with_lichess_access_token(func):
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(request: "HttpRequest", *args, **kwargs):
            lichess_access_token = (
                cookie_helpers.get_lichess_api_access_token_from_request(request)
            )
            return await func(
                request, *args, lichess_access_token=lichess_access_token, **kwargs
            )

    else:

        @functools.wraps(func)
        def wrapper(request: "HttpRequest", *args, **kwargs):
            lichess_access_token = (
                cookie_helpers.get_lichess_api_access_token_from_request(request)
            )
            return func(
                request, *args, lichess_access_token=lichess_access_token, **kwargs
            )

    return wrapper


def with_user_prefs(func):
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(request: "HttpRequest", *args, **kwargs):
            user_prefs = get_user_prefs_from_request(request)
            return await func(request, *args, user_prefs=user_prefs, **kwargs)

    else:

        @functools.wraps(func)
        def wrapper(request: "HttpRequest", *args, **kwargs):
            user_prefs = get_user_prefs_from_request(request)
            return func(request, *args, user_prefs=user_prefs, **kwargs)

    return wrapper


def redirect_if_no_lichess_access_token(func):
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(
            request: "HttpRequest",
            *args,
            lichess_access_token: "LichessAccessToken | None",
            **kwargs,
        ):
            if not lichess_access_token:
                return redirect("lichess_bridge:homepage")
            return await func(
                request, *args, lichess_access_token=lichess_access_token, **kwargs
            )

    else:

        @functools.wraps(func)
        def wrapper(
            request: "HttpRequest",
            *args,
            lichess_access_token: "LichessAccessToken | None",
            **kwargs,
        ):
            if not lichess_access_token:
                return redirect("lichess_bridge:homepage")
            return func(
                request, *args, lichess_access_token=lichess_access_token, **kwargs
            )

    return wrapper


def handle_chess_logic_exceptions(func):
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ChessLogicException as exc:
                raise BadRequest(str(exc)) from exc

    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ChessLogicException as exc:
                raise BadRequest(str(exc)) from exc

    return wrapper
