from typing import TYPE_CHECKING
from unittest import mock

import pytest
import time_machine

from ._helpers import (
    get_today_server_stats,
    play_bot_move,
    play_player_move,
    start_new_attempt,
)

if TYPE_CHECKING:
    from django.test import Client as DjangoClient

    from apps.chess.types import MoveTuple

    from ..models import DailyChallenge


@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_server_stats_played_challenges_count(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
    cleared_django_default_cache,
):
    # TODO: simplify this test? 😅
    get_current_challenge_mock.return_value = challenge_minimalist

    def sut() -> int:
        return get_today_server_stats().played_challenges_count

    def play_first_2_turns(expected_played_challenges_count: int) -> None:
        play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]
        assert sut() == expected_played_challenges_count

        # player 1st move:
        player_move_1: "MoveTuple" = ("a1", "b1")
        play_player_move(client, player_move_1)
        assert sut() == expected_played_challenges_count

        bot_move: "MoveTuple" = ("a7", "a6")
        play_bot_move(client, bot_move)
        assert sut() == expected_played_challenges_count

        # player 2nd move:
        player_move_2: "MoveTuple" = ("b1", "a1")
        play_player_move(client, player_move_2)

    def play_day_session():
        """We'll play 2 sessions on the same day, with 2 attempts on each session."""
        for play_session_expected_data in (
            {
                "played_challenges_count_at_start": 0,
                # That's the only time the count should be incremented, as it will be
                # our first play session of the day:
                "played_challenges_count_at_end": 1,
            },
            {
                "played_challenges_count_at_start": 1,
                "played_challenges_count_at_end": 1,
            },
        ):
            played_challenges_count_at_start, played_challenges_count_at_end = (
                play_session_expected_data["played_challenges_count_at_start"],
                play_session_expected_data["played_challenges_count_at_end"],
            )

            client.get("/")
            assert sut() == played_challenges_count_at_start

            # Play the first 2 turns for the 1st time of the day...
            play_first_2_turns(played_challenges_count_at_start)
            # ...and check that the `played_challenges_count` has been incremented:
            assert sut() == played_challenges_count_at_end

            # Now let's trigger a new attempt:
            start_new_attempt(client)

            # Play the same first 2 turns...
            play_first_2_turns(played_challenges_count_at_end)
            # ...and check that the `played_challenges_count` has *not* been incremented:
            assert sut() == played_challenges_count_at_end

            # Finish with a new attempt:
            start_new_attempt(client)

    with time_machine.travel("2023-03-16"):
        play_day_session()

    # Now let's do the same thing, but on a different day, in order to check that our
    # "daily challenge stats" are indeed "daily":
    with time_machine.travel("2023-03-17"):
        play_day_session()


@pytest.mark.parametrize(
    ("previous_game_date", "expected_returning_players_count"),
    (
        # N.B. The new game will be played on "2023-03-17"
        (None, 0),
        # Even a long time ago should be considered as a returning player:
        ("2023-01-01", 1),
        # So is yesterday:
        ("2023-03-16", 1),
    ),
)
@mock.patch("apps.daily_challenge.business_logic.get_current_daily_challenge")
@pytest.mark.django_db
def test_server_stats_returning_players_count(
    # Mocks
    get_current_challenge_mock: mock.MagicMock,
    # Test dependencies
    challenge_minimalist: "DailyChallenge",
    client: "DjangoClient",
    cleared_django_default_cache,
    # Test parameters
    previous_game_date: str | None,
    expected_returning_players_count: int,
):
    get_current_challenge_mock.return_value = challenge_minimalist

    def sut() -> int:
        return get_today_server_stats().returning_players_count

    if previous_game_date:
        with time_machine.travel(previous_game_date):
            client.get("/")

    with time_machine.travel("2023-03-17"):
        client.get("/")

        assert sut() == 0

        play_bot_move(client, challenge_minimalist.bot_first_move)  # type: ignore[arg-type]
        assert sut() == 0

        # player 1st move:
        player_move_1: "MoveTuple" = ("a1", "b1")
        play_player_move(client, player_move_1)
        assert sut() == 0

        bot_move: "MoveTuple" = ("a7", "a6")
        play_bot_move(client, bot_move)
        assert sut() == 0

        # player 2nd move:
        # --> that's where we keep a record of whether it's a returning player or not
        player_move_2: "MoveTuple" = ("b1", "a1")
        play_player_move(client, player_move_2)
        assert sut() == expected_returning_players_count
