from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


def test_lichess_homepage_no_access_token_smoke_test(client: "DjangoClient"):
    """Just a quick smoke test for now"""

    response = client.get("/lichess/")
    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" in response_html
    assert "Log out from Lichess" not in response_html


@mock.patch("apps.lichess_bridge.lichess_api._create_lichess_api_client")
def test_lichess_homepage_with_access_token_smoke_test(
    create_lichess_api_client_mock: mock.MagicMock, client: "DjangoClient"
):
    """Just a quick smoke test for now"""

    create_lichess_api_client_mock.return_value.account.get.return_value = {
        "username": "ChessChampion"
    }

    client.cookies["lichess.access_token"] = "lio_123456"
    response = client.get("/lichess/")
    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode("utf-8")
    assert "Log in via Lichess" not in response_html
    assert "Log out from Lichess" in response_html
    assert "ChessChampion" in response_html

    create_lichess_api_client_mock.assert_called_once_with("lio_123456")
