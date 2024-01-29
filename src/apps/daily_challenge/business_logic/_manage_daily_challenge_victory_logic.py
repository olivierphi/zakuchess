from math import ceil
from typing import TYPE_CHECKING, cast

from django.utils.timezone import now

from ..consts import MAXIMUM_TURNS_PER_CHALLENGE
from ..models import PlayerGameOverState, PlayerStats

if TYPE_CHECKING:
    from typing import Literal

    from ..models import PlayerGameState


def manage_daily_challenge_victory_logic(
    *, game_state: "PlayerGameState", stats: PlayerStats
) -> None:
    """
    When a player wins a new daily challenge, we need to update part of their stats
    and their game state.
    """

    assert game_state.game_over == PlayerGameOverState.WON

    # One more game won for this player! Happy stats :-)
    stats.win_count += 1

    # Whether the current streak was at zero or not, increment the current streak
    stats.current_streak += 1

    # Max streak management:
    if stats.current_streak > stats.max_streak:
        stats.max_streak = stats.current_streak

    # Now that we've used it to determine the streak, we can update the `last_won` date:
    stats.last_won = now().date()

    # Wins distribution management:
    total_turns = game_state.turns_counter
    # This gives us a number between 1 and 5, where 1 is the best performance and 5 the worst:
    distribution_slice = cast(
        "Literal[1, 2, 3, 4, 5]",
        ceil(
            total_turns
            / MAXIMUM_TURNS_PER_CHALLENGE
            * PlayerStats.WINS_DISTRIBUTION_SLICE_COUNT
        ),
    )
    assert 1 <= distribution_slice <= PlayerStats.WINS_DISTRIBUTION_SLICE_COUNT, (
        f"Unexpected distribution slice: {distribution_slice} "
        f"(turns_counter={game_state.turns_counter}, distribution_slice={distribution_slice})"
    )
    stats.wins_distribution[distribution_slice] += 1
