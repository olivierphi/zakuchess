import re
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal

from django.utils.timezone import now

from apps.chess.helpers import uci_move_squares

from ..models import DailyChallengeStats, PlayerSessionContent

if TYPE_CHECKING:
    from django.http import HttpResponse
    from django.test import Client as DjangoClient

    from apps.chess.types import MoveTuple

_PIECE_SELECTION_PATTERN = re.compile(
    r"""data-hx-get="/htmx/pieces/[a-f][1-8]/select/"""
)


def assert_response_waiting_for_bot_move(response: "HttpResponse") -> None:
    response_html = response.content.decode()
    assert_response_contains_a_bot_move_to_play(response_html)
    assert_response_does_not_contain_pieces_selection(response_html)


def assert_response_contains_a_bot_move_to_play(response_content: str) -> None:
    assert "playBotMove(" in response_content
    assert "Waiting for opponent's turn" in response_content


def assert_response_does_not_contain_pieces_selection(response_content: str) -> None:
    assert _PIECE_SELECTION_PATTERN.search(response_content) is None


def play_player_move(
    client: "DjangoClient",
    move: "str | MoveTuple",
    *,
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> "HttpResponse":
    if isinstance(move, str):
        move = uci_move_squares(move)
    assert isinstance(move, tuple) and len(move) == 2
    player_move_url = f"/htmx/pieces/{move[0]}/move/{move[1]}/"
    response = client.post(player_move_url)
    assert (
        response.status_code == expected_status_code
    ), f"play_player_move({move}): {response.status_code=} (expected: {expected_status_code})"
    return response


def play_bot_move(
    client: "DjangoClient",
    move: "str | MoveTuple",
    *,
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> "HttpResponse":
    if isinstance(move, str):
        move = uci_move_squares(move)
    assert isinstance(move, tuple) and len(move) == 2
    bot_move_url = f"/htmx/bot/pieces/{move[0]}/move/{move[1]}/"
    response = client.post(bot_move_url)
    assert (
        response.status_code == expected_status_code
    ), f"play_bot_move({move}): {response.status_code=} (expected: {expected_status_code})"
    return response


def start_new_attempt(client: "DjangoClient") -> None:
    restarts_count = get_today_server_stats().restarts_count
    response = client.post("/htmx/daily-challenge/restart/do/")
    assert response.status_code == HTTPStatus.OK
    assert get_today_server_stats().restarts_count == restarts_count + 1


def play_moves(
    client: "DjangoClient",
    moves: list["MoveTuple"],
    starting_side=Literal["bot", "player"],
) -> None:
    current_side = starting_side
    for move in moves:
        play_func = play_bot_move if current_side == "bot" else play_player_move
        play_func(client, move)
        current_side = "player" if current_side == "bot" else "bot"


def get_today_server_stats() -> DailyChallengeStats:
    return DailyChallengeStats.objects.get(day=now().date())


def get_session_content(client: "DjangoClient") -> PlayerSessionContent:
    session_cookie_content: str = client.session.get("pc")
    return PlayerSessionContent.from_cookie_content(session_cookie_content)
