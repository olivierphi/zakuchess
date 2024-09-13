import contextlib
import json
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from unittest import mock

import pytest

if TYPE_CHECKING:
    from django.test import AsyncClient as DjangoAsyncClient, Client as DjangoClient


class HttpClientMockBase:
    def __init__(self, access_token):
        self.lichess_access_token = access_token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.lichess_access_token}"}


class HttpClientResponseMockBase:
    def __init__(self, path):
        self.path = path

    def raise_for_status(self):
        pass


def test_lichess_homepage_no_access_token_smoke_test(client: "DjangoClient"):
    """Just a quick smoke test for now"""

    response = client.get("/lichess/")
    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" in response_html
    assert "Manage your Lichess account" not in response_html


@pytest.mark.django_db  # just because we use the DatabaseCache
async def test_lichess_homepage_with_access_token_smoke_test(
    async_client: "DjangoAsyncClient",
    acleared_django_default_cache,
):
    """Just a quick smoke test for now"""

    access_token = "lio_123456789"
    async_client.cookies["lichess.access_token"] = access_token

    class HttpClientMock(HttpClientMockBase):
        class HttpClientResponseMock(HttpClientResponseMockBase):
            @property
            def content(self) -> str:
                # The client's response's `content` is a property
                result: dict[str, Any] = {}
                match self.path:
                    case "/api/account":
                        result = {
                            "id": "chesschampion",
                            "url": "https://lichess.org/@/chesschampion",
                            "username": "ChessChampion",
                        }
                    case "/api/account/playing":
                        result = {"nowPlaying": []}
                    case _:
                        raise ValueError(f"Unexpected path: {self.path}")
                return json.dumps(result)

        async def get(self, path, **kwargs):
            # The client's `get` method is async
            assert path.startswith("/api/")
            return self.HttpClientResponseMock(path)

    with mock.patch(
        "apps.lichess_bridge.lichess_api._create_lichess_api_client",
    ) as create_lichess_api_client_mock:
        create_lichess_api_client_mock.return_value.__aenter__.return_value = (
            HttpClientMock(access_token)
        )

        response = await async_client.get("/lichess/")

        assert create_lichess_api_client_mock.call_count == 1

    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" not in response_html
    assert "Manage your Lichess account" in response_html
    assert "ChessChampion" in response_html


async def test_lichess_create_game_without_access_token_should_redirect(
    async_client: "DjangoAsyncClient",
):
    response = await async_client.get("/lichess/games/new/")

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db  # just because we use the DatabaseCache
async def test_lichess_create_game_with_access_token_smoke_test(
    async_client: "DjangoAsyncClient",
):
    """Just a quick smoke test for now"""

    access_token = "lio_123456789"
    async_client.cookies["lichess.access_token"] = access_token

    response = await async_client.get("/lichess/games/new/")

    assert response.status_code == HTTPStatus.OK


async def test_lichess_correspondence_game_without_access_token_should_redirect(
    async_client: "DjangoAsyncClient",
):
    response = await async_client.get("/lichess/games/correspondence/tFXGsEvq/")

    assert response.status_code == HTTPStatus.FOUND


_LICHESS_CORRESPONDENCE_GAME_FROM_STREAM_JSON_RESPONSE = {
    "id": "tFfGsEpb",
    "variant": {"key": "standard", "name": "Standard", "short": "Std"},
    "speed": "correspondence",
    "perf": {"name": "Correspondence"},
    "rated": False,
    "createdAt": 1725637044590,
    "white": {
        "id": "chesschampion",
        "name": "ChessChampion",
        "title": None,
        "rating": 1500,
        "provisional": True,
    },
    "black": {
        "id": "chessmaster74960",
        "name": "ChessMaster74960",
        "title": None,
        "rating": 2078,
    },
    "initialFen": "startpos",
    "daysPerTurn": 3,
    "type": "gameFull",
    "state": {
        "type": "gameState",
        "moves": "e2e4 d7d5 f2f3 e7e5 f1d3 f8c5 b2b3",
        "wtime": 259200000,
        "btime": 255151000,
        "winc": 0,
        "binc": 0,
        "status": "started",
    },
}

_LICHESS_CORRESPONDENCE_GAME_EXPORT_JSON_RESPONSE = {
    "id": "tFfGsEpb",
    "fullId": "tFfGsEpbd0mL",
    "rated": False,
    "variant": "standard",
    "speed": "correspondence",
    "perf": "correspondence",
    "createdAt": 1725637044590,
    "lastMoveAt": 1725714989179,
    "status": "started",
    "source": "lobby",
    "players": {
        "white": {
            "user": {"name": "ChessChampion", "id": "chesschampion"},
            "rating": 1500,
            "provisional": True,
        },
        "black": {
            "user": {"name": "ChessMaster74960", "id": "chessmaster74960"},
            "rating": 2078,
        },
    },
    "opening": {"eco": "B01", "name": "Scandinavian Defense", "ply": 2},
    "moves": "e4 d5",
    "pgn": "\n".join(
        # https://en.wikipedia.org/wiki/Portable_Game_Notation
        (
            '[Event "Casual correspondence game"]',
            '[Site "https://lichess.org/tFXGsEcq"]',
            '[Date "2024.09.06"]',
            '[White "ChessChampion"]',
            '[Black "ChessMaster74960"]',
            '[Result "*"]',
            '[UTCDate "2024.09.06"]',
            '[UTCTime "15:37:24"]',
            '[WhiteElo "1500"]',
            '[BlackElo "2078"]',
            '[Variant "Standard"]',
            '[TimeControl "-"]',
            '[ECO "B01"]',
            '[Opening "Scandinavian Defense"]',
            '[Termination "Unterminated"]',
            "\n1. e4 d5 *",
            "\n\n",
        )
    ),
    "daysPerTurn": 3,
    "division": {},
}


@pytest.mark.django_db  # just because we use the DatabaseCache
async def test_lichess_correspondence_game_with_access_token_smoke_test(
    async_client: "DjangoAsyncClient",
    acleared_django_default_cache,
):
    """Just a quick smoke test for now"""

    access_token = "lio_123456789"
    async_client.cookies["lichess.access_token"] = access_token

    class HttpClientMock(HttpClientMockBase):
        class HttpClientResponseMock(HttpClientResponseMockBase):
            @property
            def content(self) -> str:
                # The client's response's `content` is a property
                result: dict[str, Any] = {}
                match self.path:
                    case "/api/account":
                        result = {
                            "id": "chesschampion",
                            "url": "https://lichess.org/@/chesschampion",
                            "username": "ChessChampion",
                        }
                    case _:
                        raise ValueError(f"Unexpected path: {self.path}")
                return json.dumps(result)

            async def aiter_lines(self):
                yield json.dumps(_LICHESS_CORRESPONDENCE_GAME_FROM_STREAM_JSON_RESPONSE)
                raise ValueError(
                    "aiterlines should be stopped after the 1st line was read"
                )

        async def get(self, path, **kwargs):
            # The client's `get` method is async
            assert path.startswith("/api/")
            return self.HttpClientResponseMock(path)

        @contextlib.asynccontextmanager
        async def stream(self, method, path, **kwargs):
            assert method == "GET" and path.startswith("/api/board/game/stream/")
            yield self.HttpClientResponseMock(path)

    with mock.patch(
        "apps.lichess_bridge.lichess_api._create_lichess_api_client",
    ) as create_lichess_api_client_mock:
        client_mock = HttpClientMock(access_token)
        create_lichess_api_client_mock.return_value.__aenter__.return_value = (
            client_mock
        )

        response = await async_client.get("/lichess/games/correspondence/tFfGsEpb/")

        assert create_lichess_api_client_mock.call_count == 1

    assert response.status_code == HTTPStatus.OK
