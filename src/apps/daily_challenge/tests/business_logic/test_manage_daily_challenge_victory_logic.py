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


@pytest.mark.parametrize(
    ("turns_counter", "expected_wins_distribution"),
    (
        # We have 5 tiers of performance, and 40 turns to win a game,
        # so each tier is 8 turns long.
        (40, [0, 0, 0, 0, 1]),  # let's start with the maximum number of turns to win
        (5, [1, 0, 0, 0, 0]),  # very quick victory: --> first tier!
        (8, [1, 0, 0, 0, 0]),  # victory at the upper bound of the 1st tier
        (9, [0, 1, 0, 0, 0]),  # 2nd tier victory, lower bound
        (16, [0, 1, 0, 0, 0]),  # ditto, upper bound
        (17, [0, 0, 1, 0, 0]),  # 3rd tier victory, lower bound
        (24, [0, 0, 1, 0, 0]),  # ditto, upper bound
        (25, [0, 0, 0, 1, 0]),  # 3rd tier victory, lower bound
        (32, [0, 0, 0, 1, 0]),  # ditto, upper bound
        (33, [0, 0, 0, 0, 1]),  # 4th tier victory, lower bound
    ),
)
@mock.patch("apps.daily_challenge.models.DailyChallengeStats.objects", mock.MagicMock())
def test_manage_daily_challenge_victory_logic_wins_distribution(
    # Test dependencies
    dummy_daily_challenge,
    player_game_state_minimalist: PlayerGameState,
    # Test parameters
    turns_counter: int,
    expected_wins_distribution: list[int],
):
    game_state = player_game_state_minimalist
    game_state.turns_counter = turns_counter
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
