import contextlib
import datetime as dt
import logging
import time
from typing import TYPE_CHECKING
from zlib import adler32

import httpx
import msgspec
from django.conf import settings
from django.core.cache import cache

from .models import (
    LICHESS_ACCESS_TOKEN_PREFIX,
    LichessAccountInformation,
    LichessGameExport,
    LichessGameFullFromStream,
    LichessOngoingGameData,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from apps.chess.types import Square

    from .models import LichessAccessToken, LichessGameId, LichessGameSeekId

_logger = logging.getLogger(__name__)


_GET_MY_ACCOUNT_CACHE = {
    "KEY_PATTERN": "lichess_bridge::get_my_account::{lichess_access_token_hash}",
    "DURATION": dt.timedelta(seconds=120).total_seconds(),
}

_GET_GAME_BY_ID_FROM_STREAM_CACHE = {
    "KEY_PATTERN": "lichess_bridge::get_game_by_id_from_stream::{game_id}",
    "DURATION": dt.timedelta(seconds=30).total_seconds(),
}

_GET_EXPORT_BY_ID_CACHE = {
    "KEY_PATTERN": "lichess_bridge::get_game_export_by_id::{game_id}",
    "DURATION": dt.timedelta(seconds=30).total_seconds(),
}


def is_lichess_api_access_token_valid(token: str) -> bool:
    return token.startswith(LICHESS_ACCESS_TOKEN_PREFIX) and len(token) > 10


async def get_my_account(*, api_client: httpx.AsyncClient) -> LichessAccountInformation:
    """
    This is cached for a short amount of time.
    """
    # Let's not expose any access tokens in our cache keys, and instead use a quick hash
    # of the "Authorization" header (which contains the token).
    # "An Adler-32 checksum is almost as reliable as a CRC32 but can be computed much more quickly."
    # --> should be enough for our case :-)
    lichess_access_token_hash = adler32(api_client.headers["Authorization"].encode())

    cache_key = _GET_MY_ACCOUNT_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        lichess_access_token_hash=lichess_access_token_hash
    )
    if cached_data := await cache.aget(cache_key):
        _logger.info("Using cached data for 'get_my_account'.")
        response_content = cached_data
    else:
        # https://lichess.org/api#tag/Account/operation/accountMe
        endpoint = "/api/account"
        with _lichess_api_monitoring("GET", endpoint):
            response = await api_client.get(endpoint)
            response.raise_for_status()

        response_content = response.content
        await cache.aset(cache_key, response_content, _GET_MY_ACCOUNT_CACHE["DURATION"])

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
        response.raise_for_status()

    class ResponseDataWrapper(msgspec.Struct):
        """The ongoing games are wrapped in a "nowPlaying" root object's key"""

        nowPlaying: list[LichessOngoingGameData]

    return msgspec.json.decode(response.content, type=ResponseDataWrapper).nowPlaying


async def get_game_export_by_id(
    *,
    api_client: httpx.AsyncClient,
    game_id: "LichessGameId",
    try_fetching_from_cache: bool = True,
) -> LichessGameExport:
    """
    This is cached for a short amount of time, so we don't re-fetch the same games again
    while the player is selecting pieces.
    """
    cache_key = _GET_EXPORT_BY_ID_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        game_id=game_id,
    )

    response_content: bytes | None = None
    if try_fetching_from_cache:
        if cached_data := await cache.aget(cache_key):
            _logger.info("Using cached data for 'get_game_export_by_id'.")
            response_content = cached_data

    if not response_content:
        # https://lichess.org/api#tag/Games/operation/gamePgn
        # An important aspect to keep in mind:
        # > Ongoing games are delayed by a few seconds ranging from 3 to 60
        # > depending on the time control, as to prevent cheat bots from using this API.
        endpoint = f"/game/export/{game_id}"
        with _lichess_api_monitoring("GET", endpoint):
            # We only need the FEN, but it seems that the Lichess "game by ID" API endpoints
            # can only return the full PGN - which will require a bit more work to parse.
            response = await api_client.get(
                endpoint,
                params={"pgnInJson": "1", "tags": "0", "moves": "0", "evals": "0"},
            )
            response.raise_for_status()

        response_content = response.content
        await cache.aset(
            cache_key, response_content, _GET_EXPORT_BY_ID_CACHE["DURATION"]
        )

    return msgspec.json.decode(response_content, type=LichessGameExport)


async def get_game_by_id_from_stream(
    *,
    api_client: httpx.AsyncClient,
    game_id: "LichessGameId",
    try_fetching_from_cache: bool = True,
) -> LichessGameFullFromStream:
    """
    This is cached for a short amount of time, so we don't re-fetch the same games again
    while the player is selecting pieces.
    """
    cache_key = _GET_GAME_BY_ID_FROM_STREAM_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        game_id=game_id,
    )

    response_content: str | None = None
    if try_fetching_from_cache:
        if cached_data := await cache.aget(cache_key):
            _logger.info("Using cached data for 'get_game_by_id_from_stream'.")
            response_content = cached_data

    if not response_content:
        # https://lichess.org/api#tag/Board/operation/boardGameStream
        endpoint = f"/api/board/game/stream/{game_id}"
        with _lichess_api_monitoring("GET (stream)", endpoint):
            async with api_client.stream("GET", endpoint) as response:
                async for line in response.aiter_lines():
                    if line and '"gameFull"' in line:
                        response_content = line
                        # We got what we need, let's break that loop - HTTPX will
                        # automatically close the stream as we exit the `.stream` block.
                        break
            response.raise_for_status()

        await cache.aset(
            cache_key, response_content, _GET_GAME_BY_ID_FROM_STREAM_CACHE["DURATION"]
        )

    assert type(response_content) == str  # for type checkers
    return msgspec.json.decode(response_content, type=LichessGameFullFromStream)


async def clear_game_by_id_cache(game_id: "LichessGameId") -> None:
    get_game_by_id_cache_key = _GET_EXPORT_BY_ID_CACHE["KEY_PATTERN"].format(  # type: ignore[attr-defined]
        game_id=game_id,
    )
    await cache.adelete(get_game_by_id_cache_key)


async def move_lichess_game_piece(
    *,
    api_client: httpx.AsyncClient,
    game_id: "LichessGameId",
    from_: "Square",
    to: "Square",
    offering_draw: bool = False,
) -> bool:
    """
    Calling this function will make a move in a Lichess game.
    As a side effect, it will also clear the `get_game_by_id` cache for that game.
    """
    # https://lichess.org/api#tag/Board/operation/boardGameMove
    move_uci = f"{from_}{to}"
    endpoint = f"/api/board/game/{game_id}/move/{move_uci}"
    with _lichess_api_monitoring("POST", endpoint):
        response = await api_client.post(
            endpoint, params={"offeringDraw": "true"} if offering_draw else None
        )
        response.raise_for_status()

    await clear_game_by_id_cache(game_id)

    return response.json()["ok"]


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
        response.raise_for_status()

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

    return client
