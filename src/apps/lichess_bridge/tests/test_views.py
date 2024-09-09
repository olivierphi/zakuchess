import json
from http import HTTPStatus
from typing import TYPE_CHECKING, Any
from unittest import mock

if TYPE_CHECKING:
    from django.test import AsyncClient as DjangoAsyncClient, Client as DjangoClient


def test_lichess_homepage_no_access_token_smoke_test(client: "DjangoClient"):
    """Just a quick smoke test for now"""

    response = client.get("/lichess/")
    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" in response_html
    assert "Log out from Lichess" not in response_html


async def test_lichess_homepage_with_access_token_smoke_test(
    async_client: "DjangoAsyncClient",
):
    """Just a quick smoke test for now"""

    access_token = "lio_123456789"
    async_client.cookies["lichess.access_token"] = access_token

    class HttpClientMock:
        class HttpClientResponseMock:
            def __init__(self, path):
                self.path = path

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
            HttpClientMock()
        )

        response = await async_client.get("/lichess/")

        assert create_lichess_api_client_mock.call_count == 1

    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" not in response_html
    assert "disconnect your Lichess account" in response_html
    assert "ChessChampion" in response_html


async def test_lichess_create_game_without_access_token_should_redirect(
    async_client: "DjangoAsyncClient",
):
    response = await async_client.get("/lichess/games/new/")

    assert response.status_code == HTTPStatus.FOUND


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


_LICHESS_CORRESPONDENCE_GAME_JSON_RESPONSE = {
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
    "pgn": '[Event "Casual correspondence game"]\n[Site "https://lichess.org/tFXGsEcq"]\n[Date "2024.09.06"]\n[White "ChessChampion"]\n[Black "ChessMaster74960"]\n[Result "*"]\n[UTCDate "2024.09.06"]\n[UTCTime "15:37:24"]\n[WhiteElo "1500"]\n[BlackElo "2078"]\n[Variant "Standard"]\n[TimeControl "-"]\n[ECO "B01"]\n[Opening "Scandinavian Defense"]\n[Termination "Unterminated"]\n\n1. e4 d5 *\n\n\n',
    "daysPerTurn": 3,
    "division": {},
}


async def test_lichess_correspondence_game_with_access_token_smoke_test(
    async_client: "DjangoAsyncClient",
):
    """Just a quick smoke test for now"""

    access_token = "lio_123456789"
    async_client.cookies["lichess.access_token"] = access_token

    class HttpClientMock:
        class HttpClientResponseMock:
            def __init__(self, path):
                self.path = path

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
                    case "/game/export/tFfGsEpb":
                        result = _LICHESS_CORRESPONDENCE_GAME_JSON_RESPONSE
                    case _:
                        raise ValueError(f"Unexpected path: {self.path}")
                return json.dumps(result)

        async def get(self, path, **kwargs):
            # The client's `get` method is async
            assert path.startswith(("/api/", "/game/export/"))
            return self.HttpClientResponseMock(path)

    with mock.patch(
        "apps.lichess_bridge.lichess_api._create_lichess_api_client",
    ) as create_lichess_api_client_mock:
        create_lichess_api_client_mock.return_value.__aenter__.return_value = (
            HttpClientMock()
        )

        response = await async_client.get("/lichess/games/correspondence/tFfGsEpb/")

        assert create_lichess_api_client_mock.call_count == 1

    assert response.status_code == HTTPStatus.OK
