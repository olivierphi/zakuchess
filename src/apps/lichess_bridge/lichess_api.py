import contextlib
import datetime as dt
import logging
import time
from typing import TYPE_CHECKING

import httpx
import msgspec
from django.conf import settings
from django.core.cache import cache

from .models import (
    LICHESS_ACCESS_TOKEN_PREFIX,
    LichessAccountInformation,
    LichessGameExport,
    LichessOngoingGameData,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .models import LichessAccessToken, LichessGameSeekId

_logger = logging.getLogger(__name__)


_GET_MY_ACCOUNT_CACHE = {
    "KEY_PATTERN": "lichess_bridge::get_my_account::{lichess_access_token}",
    "DURATION": dt.timedelta(seconds=120).total_seconds(),
}

_GET_GAME_BY_ID_CACHE = {
    "KEY_PATTERN": "lichess_bridge::get_game_by_id::{lichess_access_token}::{game_id}",
    "DURATION": dt.timedelta(seconds=30).total_seconds(),
}


def is_lichess_api_access_token_valid(token: str) -> bool:
    return token.startswith(LICHESS_ACCESS_TOKEN_PREFIX) and len(token) > 10


async def get_my_account(*, api_client: httpx.AsyncClient) -> LichessAccountInformation:
    """
    This is cached for a short amount of time.
    """
    cache_key = _GET_MY_ACCOUNT_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        lichess_access_token=api_client.lichess_access_token  # type: ignore[attr-defined]
    )
    if cached_data := cache.get(cache_key):
        _logger.info("Using cached data for 'get_my_account'.")
        response_content = cached_data
    else:
        # https://lichess.org/api#tag/Account/operation/accountMe
        endpoint = "/api/account"
        with _lichess_api_monitoring("GET", endpoint):
            response = await api_client.get(endpoint)

        response_content = response.content
        cache.set(cache_key, response_content, _GET_MY_ACCOUNT_CACHE["DURATION"])

    return msgspec.json.decode(response_content, type=LichessAccountInformation)


async def get_my_ongoing_games(
    *,
    api_client: httpx.AsyncClient,
    count: int = 5,
) -> list[LichessOngoingGameData]:
    # https://lichess.org/api#tag/Games/operation/apiAccountPlaying
    endpoint = "/api/account/playing"
    with _lichess_api_monitoring("GET", endpoint):
        response = await api_client.get(endpoint, params={"nb": count})

    class ResponseDataWrapper(msgspec.Struct):
        """The ongoing games are wrapped in a "nowPlaying" root object's key"""

        nowPlaying: list[LichessOngoingGameData]

    return msgspec.json.decode(response.content, type=ResponseDataWrapper).nowPlaying


async def get_game_by_id(
    *, api_client: httpx.AsyncClient, game_id: str
) -> LichessGameExport:
    """
    This is cached for a short amount of time, so we don't re-fetch the same games again
    while the player is selecting pieces.
    """
    cache_key = _GET_GAME_BY_ID_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        lichess_access_token=api_client.lichess_access_token,  # type: ignore[attr-defined]
        game_id=game_id,
    )
    if cached_data := cache.get(cache_key):
        _logger.info("Using cached data for 'get_game_by_id'.")
        response_content = cached_data
    else:
        # https://lichess.org/api#tag/Games/operation/gamePgn
        endpoint = f"/game/export/{game_id}"
        with _lichess_api_monitoring("GET", endpoint):
            # We only need the FEN, but it seems that the Lichess "game by ID" API endpoints
            # can only return the full PGN - which will require a bit more work to parse.
            response = await api_client.get(endpoint, params={"pgnInJson": "true"})

        response_content = response.content
        cache.set(cache_key, response_content, _GET_GAME_BY_ID_CACHE["DURATION"])

    return msgspec.json.decode(response_content, type=LichessGameExport)


async def create_correspondence_game(
    *, api_client: httpx.AsyncClient, days_per_turn: int
) -> "LichessGameSeekId":
    # https://lichess.org/api#tag/Board/operation/apiBoardSeek
    # TODO: give more customisation options to the user
    endpoint = "/api/board/seek"
    with _lichess_api_monitoring("POST", endpoint):
        response = await api_client.post(
            endpoint,
            json={
                "rated": False,
                "days": days_per_turn,
                "variant": "standard",
                "color": "random",
            },
        )
    return str(response.json()["id"])


def get_lichess_api_client(access_token: "LichessAccessToken") -> httpx.AsyncClient:
    return _create_lichess_api_client(access_token)


@contextlib.contextmanager
def _lichess_api_monitoring(target_endpoint, method) -> "Iterator[None]":
    start_time = time.monotonic()
    yield
    _logger.info(
        "Lichess API: %s '%s' took %ims.",
        method,
        target_endpoint,
        (time.monotonic() - start_time) * 1000,
    )


# This is the function we'll mock during tests - as it's private, we don't have to
# mind about it being directly imported by other modules when we mock it.
def _create_lichess_api_client(access_token: "LichessAccessToken") -> httpx.AsyncClient:
    client = httpx.AsyncClient(
        base_url=settings.LICHESS_HOST,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    # We store the access token in the client object, so we can access it later
    # Not super clean, but... this is a side project, and where's the joy if I cannot
    # allow myself some dirty shortcuts in such a context? 😄
    client.lichess_access_token = access_token  # type: ignore[attr-defined]

    return client
