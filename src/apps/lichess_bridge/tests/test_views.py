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
    with mock.patch(
        "apps.lichess_bridge.lichess_api._create_lichess_api_client",
    ) as create_lichess_api_client_mock:

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
                    return json.dumps(result)

            async def get(self, path, **kwargs):
                # The client's `get` method is async
                assert path.startswith("/api/")
                return self.HttpClientResponseMock(path)

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
