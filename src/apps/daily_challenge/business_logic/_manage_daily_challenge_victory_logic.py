from typing import TYPE_CHECKING

from ..types import PlayerGameOverState

if TYPE_CHECKING:
    from ..types import PlayerGameState, PlayerStats


def manage_daily_challenge_victory_logic(
    *, game_state: "PlayerGameState", stats: "PlayerStats"
) -> None:
    """
    When a player wins a new daily challenge, we need to update part of their stats
    and their game state.
    """

    game_state.game_over = PlayerGameOverState.WON

    # One more game won for this player! Happy stats :-)
    stats.win_count += 1

    # Aaaand... that's all for now, folks! :-)
