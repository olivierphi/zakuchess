from http import HTTPStatus
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import time_machine

from ..models import (
    PlayerGameOverState,
    PlayerGameState,
    PlayerSessionContent,
    PlayerStats,
)
from ._helpers import (
    assert_response_waiting_for_bot_move,
    get_session_content,
    play_bot_move,
)

if TYPE_CHECKING:
    from django.test import Client as DjangoClient

    from apps.chess.types import Square

    from ..models import DailyChallenge


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@time_machine.travel("2024-01-01")
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
    session_cookie_value = response.cookies["sessionid"].value
    assert 300 < len(session_cookie_value) < 325
    assert session_cookie_value.startswith(
        # This part of the signed+compressed session data is deterministic:
        ".eJx"
    )

    # As we're waiting for the bot to play its 1st turn, we should not be able to
    # select any of our pieces:
    assert_response_waiting_for_bot_move(response)

    # Ok, let's assert some stuff regarding the session cookie content:
    session_content = get_session_content(client)
    session_content_expected = PlayerSessionContent(
        encoding_version=1,
        games={
            "2024-01-01": PlayerGameState(
                attempts_counter=0,
                turns_counter=0,
                current_attempt_turns_counter=0,
                fen="1k6/pp3Q2/7p/8/8/8/7B/K7 b - - 0 1",
                piece_role_by_square={
                    "f7": "Q",
                    "b7": "p1",
                    "a7": "p2",
                    "h6": "p3",
                    "h2": "B1",
                    "a1": "K",
                    "b8": "k",
                },
                moves="",
                game_over=PlayerGameOverState.PLAYING,
            )
        },
        stats=PlayerStats(
            games_count=0,
            win_count=0,
            current_streak=0,
            max_streak=0,
            last_played=None,
            last_won=None,
            wins_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        ),
    )
    assert session_content == session_content_expected


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

    response = client.get("/")
    assert_response_waiting_for_bot_move(response)
    play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]

    response = client.get(f"/htmx/pieces/{location}/select/")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    (
        "square",
        "expected_team_member_name_display",
    ),
    (
        ("a1", "KING 1"),
        ("f7", "QUEEN 1"),
    ),
)
@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_htmx_game_select_piece_returned_html(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
    # Test parameters
    square: "Square",
    expected_team_member_name_display: str,
):
    get_current_challenge_mock.return_value = challenge_minimalist

    response = client.get("/")
    assert_response_waiting_for_bot_move(response)
    play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]

    response = client.get(f"/htmx/pieces/{square}/select/")
    assert response.status_code == HTTPStatus.OK

    response_html = response.content.decode()
    assert expected_team_member_name_display in response_html
    not_expected_team_member_names_display = {"KING 1", "QUEEN 1", "BISHOP 1"} - {
        expected_team_member_name_display
    }
    for other_team_member_name in not_expected_team_member_names_display:
        assert other_team_member_name not in response_html


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

    response = client.get("/")
    assert_response_waiting_for_bot_move(response)
    play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]

    session_content_before_player_1st_move = get_session_content(client)
    assert session_content_before_player_1st_move.stats.games_count == 0

    response = client.post(f"/htmx/pieces/{input_['from_']}/move/{input_['to']}/")
    assert response.status_code == expected_status_code

    if expected_status_code == HTTPStatus.OK:
        # Ok, let's assert some stuff regarding the session cookie content:
        session_content_after_player_1st_move = get_session_content(client)
        assert session_content_after_player_1st_move.stats.games_count == 1


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

    response = client.get("/")
    assert_response_waiting_for_bot_move(response)

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

    response = client.get("/")
    assert_response_waiting_for_bot_move(response)
    play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]

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


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_help_modal_smoke_test(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
):
    get_current_challenge_mock.return_value = challenge_minimalist

    response = client.get("/htmx/daily-challenge/modals/help/")
    assert response.status_code == HTTPStatus.OK
    response_content = response.content.decode()
    assert "How to play" in response_content
    assert "restart" in response_content
    assert "characters" in response_content
