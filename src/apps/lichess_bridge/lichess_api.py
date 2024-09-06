from typing import TYPE_CHECKING, Literal

import httpx
import msgspec
from django.conf import settings

from .models import LICHESS_ACCESS_TOKEN_PREFIX

if TYPE_CHECKING:
    from .models import LichessAccessToken, LichessGameSeekId


class AccountInformation(
    msgspec.Struct,
):
    """Information about an account, as returned by the Lichess API."""

    # N.B. There are many more fields than this - but we only use these at the moment

    id: str  # e.g.  "philippe"
    username: str  # e.g.  "Philippe"
    url: str  # e.g. "https://lichess.org/@/dunsap"


class OpponentData(msgspec.Struct):
    """Information about an opponent, as returned by the Lichess API."""

    id: str  # e.g.  "philippe"
    rating: int  # e.g. 1790
    username: str  # e.g.  "Philippe"


class OngoingGameData(msgspec.Struct):
    """Information about an ongoing game, as returned by the Lichess API."""

    gameId: str
    fullId: str
    color: Literal["white", "black"]
    fen: str
    hasMoved: bool
    isMyTurn: bool
    lastMove: str  # e.g. "b8c6"
    opponent: OpponentData
    perf: Literal["correspondence"]  # TODO: other values?
    rated: bool
    secondsLeft: int
    source: Literal["lobby", "friend"]  # TODO: other values?
    speed: Literal["correspondence"]  # TODO: other values?
    variant: dict[str, str]


def is_lichess_api_access_token_valid(token: str) -> bool:
    return token.startswith(LICHESS_ACCESS_TOKEN_PREFIX) and len(token) > 10


async def get_my_account(
    *,
    access_token: "LichessAccessToken",
) -> AccountInformation:
    async with _create_lichess_api_client(access_token) as client:
        # https://lichess.org/api#tag/Account/operation/accountMe
        response = await client.get("/api/account")
        return msgspec.json.decode(response.content, type=AccountInformation)


async def get_my_ongoing_games(
    *,
    access_token: "LichessAccessToken",
    count: int = 5,
) -> list[OngoingGameData]:
    async with _create_lichess_api_client(access_token) as client:
        # https://lichess.org/api#tag/Games/operation/apiAccountPlaying
        response = await client.get("/api/account/playing", params={"nb": count})

        class ResponseDataWrapper(msgspec.Struct):
            nowPlaying: list[OngoingGameData]

        return msgspec.json.decode(
            response.content, type=ResponseDataWrapper
        ).nowPlaying


async def create_correspondence_game(
    *, access_token: "LichessAccessToken", days_per_turn: int
) -> "LichessGameSeekId":
    async with _create_lichess_api_client(access_token) as client:
        # https://lichess.org/api#tag/Board/operation/apiBoardSeek
        # TODO: give more customisation options to the user
        response = await client.post(
            "/api/board/seek",
            json={
                "rated": False,
                "days": days_per_turn,
                "variant": "standard",
                "color": "random",
            },
        )
        return str(response.json()["id"])


# This is the function we'll mock during tests:
def _create_lichess_api_client(access_token: "LichessAccessToken") -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.LICHESS_HOST,
        headers={"Authorization": f"Bearer {access_token}"},
    )
