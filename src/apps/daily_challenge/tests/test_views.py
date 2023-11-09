from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest import mock
from urllib.parse import urlencode

import pytest

if TYPE_CHECKING:
    from django.test import Client as DjangoClient

    from ..models import DailyChallenge


@pytest.mark.parametrize(
    ("input_", "expected_status_code"),
    (
        ({"square": "a9"}, HTTPStatus.BAD_REQUEST),
        ({"square": "nope"}, HTTPStatus.BAD_REQUEST),
        ({"square": "a1"}, HTTPStatus.OK),  # my piece: can be selected
        ({"square": "a8"}, HTTPStatus.OK),  # opponent's piece: can be selected too
    ),
)
@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_htmx_game_select_piece_input_validation(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
    # Test parameters
    input_: dict,
    expected_status_code: int,
):
    get_current_challenge_mock.return_value = challenge_minimalist

    client.get("/")
    _play_bot_move(client, challenge_minimalist.bot_first_move)

    response = client.get("/htmx/pieces/select/", data=input_)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    ("input_", "expected_status_code"),
    (
        ({"from_": "a9", "to": "a8"}, HTTPStatus.BAD_REQUEST),
        ({"from_": "nope", "to": "a8"}, HTTPStatus.BAD_REQUEST),
        # my piece, valid move:
        ({"from_": "a1", "to": "b1"}, HTTPStatus.OK),
        # my piece, invalid move:
        ({"from_": "a1", "to": "a4"}, HTTPStatus.BAD_REQUEST),
        # opponent's piece, valid move:
        ({"from_": "a8", "to": "b8"}, HTTPStatus.BAD_REQUEST),
    ),
)
@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_htmx_game_move_piece_input_validation(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
    # Test parameters
    input_: dict,
    expected_status_code: int,
):
    get_current_challenge_mock.return_value = challenge_minimalist

    client.get("/")
    _play_bot_move(client, challenge_minimalist.bot_first_move)

    response = client.post(f"/htmx/pieces/{input_['from_']}/move/{input_['to']}/")
    assert response.status_code == expected_status_code


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_htmx_game_select_piece_should_fail_on_empty_square(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
):
    get_current_challenge_mock.return_value = challenge_minimalist

    client.get("/")
    _play_bot_move(client, challenge_minimalist.bot_first_move)

    empty_square = "a2"
    response = client.get("/htmx/pieces/select/", data={"square": empty_square})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def _play_bot_move(client: "DjangoClient", move) -> None:
    response = client.post(
        "/htmx/bot/move/",
        QUERY_STRING=urlencode({"move": move}, doseq=True),
    )
    assert response.status_code == HTTPStatus.OK
