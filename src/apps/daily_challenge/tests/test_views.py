from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest import mock

import pytest

if TYPE_CHECKING:
    from django.test import Client as DjangoClient

    from ..models import DailyChallenge


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_game_smoke_test(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
):
    get_current_challenge_mock.return_value = challenge_minimalist

    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert "csrftoken" in response.cookies
    assert 280 < len(response.cookies["sessionid"].value) < 310
    assert response.cookies["sessionid"].value.startswith(
        # This part of the signed+compressed session data is deterministic:
        ".eJxNkLsOgzAMRX8FeS4KCRRQR1Ym9iyQFioBbVTaMiD-vcY2qPJwffy4eSzgHVxgsXD7Wrjok4UOFdlEJgkjHRrNXDvUCPvvPXH1kbaoFnSfKu_jyqjMq5wiK1SZBU0QYkQBWuGwfzUTe7YZ7VVUbhg8D9VChuieMsVMhqiQSU1UsklO0FtYkUYCanTP7arrVpXDOycPno8HTZKMezJ4cvj_i606Y_XxGYZt-cpuWjaMaCyaiJ75-BXWH59eYVs:"
    )


@pytest.mark.parametrize(
    ("location", "expected_status_code"),
    (
        # bad move format --> our ChessSquareConverter will not let this pass
        ("a9", HTTPStatus.NOT_FOUND),
        ("nope", HTTPStatus.NOT_FOUND),
        # my piece: can be selected
        ("a1", HTTPStatus.OK),
        # opponent's piece: can be selected too
        ("a8", HTTPStatus.OK),
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
    location: str,
    expected_status_code: int,
):
    get_current_challenge_mock.return_value = challenge_minimalist

    client.get("/")
    _play_bot_move(client, challenge_minimalist.bot_first_move)

    response = client.get(f"/htmx/pieces/{location}/select/")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    ("input_", "expected_status_code"),
    (
        # bad move format --> our ChessSquareConverter will not let this pass
        ({"from_": "a9", "to": "a8"}, HTTPStatus.NOT_FOUND),
        ({"from_": "nope", "to": "a8"}, HTTPStatus.NOT_FOUND),
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


@pytest.mark.parametrize(
    ("input_", "expected_status_code"),
    (
        # bad move format --> our ChessSquareConverter will not let this pass
        ({"from_": "a7", "to": "h9"}, HTTPStatus.NOT_FOUND),
        # Not actually a move:
        ({"from_": "a8", "to": "a8"}, HTTPStatus.BAD_REQUEST),
        # Legal move, but the king is in check so cannot actually do that:
        ({"from_": "a7", "to": "a6"}, HTTPStatus.BAD_REQUEST),
        # Legal move:
        ({"from_": "b8", "to": "a8"}, HTTPStatus.OK),
    ),
)
@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_htmx_game_play_bot_move_validation(
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

    response = client.post(f"/htmx/bot/pieces/{input_['from_']}/move/{input_['to']}/")
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
    response = client.get(f"/htmx/pieces/{empty_square}/select/")
    assert response.status_code == HTTPStatus.BAD_REQUEST


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_stats_modal_smoke_test(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
):
    get_current_challenge_mock.return_value = challenge_minimalist

    response = client.get("/htmx/daily-challenge/modals/stats/")
    assert response.status_code == HTTPStatus.OK
    response_content = response.content.decode()
    assert "Statistics" in response_content


def _play_bot_move(client: "DjangoClient", move) -> None:
    bot_move_url = f"/htmx/bot/pieces/{move[0:2]}/move/{move[2:4]}/"
    response = client.post(bot_move_url)
    assert response.status_code == HTTPStatus.OK
