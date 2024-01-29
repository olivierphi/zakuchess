from typing import TYPE_CHECKING

from ..models import PlayerGameOverState

if TYPE_CHECKING:
    from ..models import PlayerGameState, PlayerStats


def manage_daily_challenge_defeat_logic(
    *, game_state: "PlayerGameState", stats: "PlayerStats"
) -> None:
    """
    When a player loses a daily challenge, we may need to update part of their game state.
    """

    assert game_state.game_over == PlayerGameOverState.LOST

    # Aaaand... that's all for now, folks! :-)
