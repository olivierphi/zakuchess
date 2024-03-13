from typing import TYPE_CHECKING, cast

from django.utils.timezone import now

from ..models import DailyChallengeStats, PlayerGameOverState, PlayerStats

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState, WinsDistributionSlice


def manage_daily_challenge_victory_logic(
    *,
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    stats: PlayerStats,
    is_preview: bool = False,
    is_staff_user: bool = False,
) -> None:
    """
    When a player wins a new daily challenge, we need to update part of their stats
    and their game state.
    """

    assert game_state.game_over == PlayerGameOverState.WON

    if is_preview:
        return None

    today = now().date()

    if stats.last_won == today:
        return  # already won today, the player is just re-trying things :-)

    # One more game won for this player! Happy stats :-)
    stats.win_count += 1

    # Whether the current streak was at zero or not, increment the current streak
    stats.current_streak += 1

    # Max streak management:
    if stats.current_streak > stats.max_streak:
        stats.max_streak = stats.current_streak

    # Now that we've used it to determine the streak, we can update the `last_won` date:
    stats.last_won = today

    # Wins distribution management:
    # This gives us a number between 1 and 5, where 1 is the best performance and 5 the worst:
    # If the number of attempts is greater than 5, we cap it to the 5th slice.
    distribution_slice = cast(
        "WinsDistributionSlice", min(5, game_state.attempts_counter + 1)
    )
    assert 1 <= distribution_slice <= PlayerStats.WINS_DISTRIBUTION_SLICE_COUNT, (
        f"Unexpected distribution slice: {distribution_slice} "
        f"(turns_counter={game_state.turns_counter}, distribution_slice={distribution_slice})"
    )
    stats.wins_distribution[distribution_slice] += 1

    # Server stats
    if not is_staff_user:
        DailyChallengeStats.objects.increment_today_wins_count()
