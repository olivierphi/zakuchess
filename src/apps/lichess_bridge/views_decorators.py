import functools
from typing import TYPE_CHECKING

from asgiref.sync import iscoroutinefunction
from django.shortcuts import redirect

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
