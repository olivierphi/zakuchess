from typing import TYPE_CHECKING

from ..types import PlayerGameOverState

if TYPE_CHECKING:
    from ..types import PlayerGameState, PlayerStats


def manage_daily_challenge_defeat_logic(
    *, game_state: "PlayerGameState", stats: "PlayerStats"
) -> None:
    """
    When a player loses a daily challenge, we need to update part of their game state.
    """

    game_state.game_over = PlayerGameOverState.LOST

    # Aaaand... that's all for now, folks! :-)
