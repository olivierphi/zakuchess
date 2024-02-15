import datetime as dt
from unittest import mock

import pytest
import time_machine

from ...business_logic import (
    manage_daily_challenge_victory_logic,
    manage_new_daily_challenge_stats_logic,
)
from ...models import PlayerGameOverState, PlayerGameState, PlayerStats

# N.B. We mock `DailyChallengeStats.objects` in these tests, because the stats logic
# is not relevant to the tests we're writing here - also, let's not summon the database
# when we can avoid it, right? :-)


@pytest.fixture
def dummy_daily_challenge():
    # All the `manage_daily_challenge_victory_logic` needs from a DailyChallenge is its
    # `max_turns_count` attribute, so let's mock only this:
    return mock.Mock(max_turns_count=40)


@mock.patch("apps.daily_challenge.models.DailyChallengeStats.objects", mock.MagicMock())
def test_manage_daily_challenge_victory_wins_count(
    # Test dependencies
    dummy_daily_challenge,
    player_game_state_minimalist: PlayerGameState,
):
    game_state = player_game_state_minimalist
    game_state.turns_counter = 8
    game_state.game_over = PlayerGameOverState.WON
    stats = PlayerStats()

    assert stats.win_count == 0

    # Go!
    manage_daily_challenge_victory_logic(
        challenge=dummy_daily_challenge, game_state=game_state, stats=stats
    )

    # Alright, let's check the results:
    assert stats.win_count == 1

    # If we win again on the same day (because we're just re-trying things), the win
    # should not be counted again:
    manage_daily_challenge_victory_logic(
        challenge=dummy_daily_challenge, game_state=game_state, stats=stats
    )
    assert stats.win_count == 1


@pytest.mark.parametrize(
    ("attempts_counter", "expected_wins_distribution"),
    (
        (0, [1, 0, 0, 0, 0]),  # very quick victory: --> first tier!
        (1, [0, 1, 0, 0, 0]),  # 2nd tier victory
        (2, [0, 0, 1, 0, 0]),  # 3rd tier victory
        (3, [0, 0, 0, 1, 0]),  # 4th tier victory
        (4, [0, 0, 0, 0, 1]),  # 5th tier victory
        (5, [0, 0, 0, 0, 1]),  # capped at 5 tiers
        (6, [0, 0, 0, 0, 1]),  # yes, still capped at 5
        (250, [0, 0, 0, 0, 1]),  # REALLY
    ),
)
@mock.patch("apps.daily_challenge.models.DailyChallengeStats.objects", mock.MagicMock())
def test_manage_daily_challenge_victory_logic_wins_distribution(
    # Test dependencies
    dummy_daily_challenge,
    player_game_state_minimalist: PlayerGameState,
    # Test parameters
    attempts_counter: int,
    expected_wins_distribution: list[int],
):
    game_state = player_game_state_minimalist
    game_state.attempts_counter = attempts_counter
    game_state.game_over = PlayerGameOverState.WON
    stats = PlayerStats()

    # Go!
    manage_daily_challenge_victory_logic(
        challenge=dummy_daily_challenge, game_state=game_state, stats=stats
    )

    # Alright, let's check the results:
    assert list(stats.wins_distribution.values()) == expected_wins_distribution


@pytest.mark.parametrize(
    (
        "current_streak",
        "max_streak",
        "last_won_date",
        "now_date",
        "expected_current_streak",
        "expected_max_streak",
    ),
    (
        # No streak yet. we're just warming up:
        (0, 0, None, "2024-01-21", 1, 1),
        (0, 0, "2024-01-20", "2024-01-21", 1, 1),
        (0, 0, "2024-01-19", "2024-01-21", 1, 1),
        # Streak in progress
        (4, 4, "2024-01-20", "2024-01-21", 5, 5),  # current & max streaks incremented
        (2, 4, "2024-01-20", "2024-01-21", 3, 4),  # only current streak incremented
        (4, 4, "2024-01-19", "2024-01-21", 1, 4),  # more than a day ago: back to 1
    ),
)
@mock.patch("apps.daily_challenge.models.DailyChallengeStats.objects", mock.MagicMock())
def test_manage_daily_challenge_victory_logic_streak_management(
    # Test dependencies
    dummy_daily_challenge,
    player_game_state_minimalist: PlayerGameState,
    # Test parameters
    current_streak: int,
    max_streak: int,
    last_won_date: str | None,
    now_date: str,
    expected_current_streak: int,
    expected_max_streak: int,
):
    player_game_state_minimalist.turns_counter = 1
    player_game_state_minimalist.game_over = PlayerGameOverState.WON

    stats = PlayerStats(
        current_streak=current_streak,
        max_streak=max_streak,
        last_won=dt.date.fromisoformat(last_won_date) if last_won_date else None,
    )

    # Go!
    with time_machine.travel(dt.date.fromisoformat(now_date)):
        # Start a game...
        manage_new_daily_challenge_stats_logic(stats=stats)
        # ...and win it, straight away! ✌
        manage_daily_challenge_victory_logic(
            challenge=dummy_daily_challenge,
            game_state=player_game_state_minimalist,
            stats=stats,
        )

    # Alright, let's check the results:
    assert stats.current_streak == expected_current_streak
    assert stats.max_streak == expected_max_streak
