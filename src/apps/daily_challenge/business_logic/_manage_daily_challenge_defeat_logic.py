from typing import TYPE_CHECKING

from ..models import PlayerGameOverState

if TYPE_CHECKING:
    from ..models import PlayerGameState


def manage_daily_challenge_defeat_logic(
    *, game_state: "PlayerGameState", is_preview: bool = False
) -> None:
    """
    When a player loses a daily challenge, we may need to update part of their game state.
    """

    assert game_state.game_over == PlayerGameOverState.LOST

    if is_preview:
        return None

    # Aaaand... that's actually all for now, folks! :-)
    # (We may want to add some stats updates here in the future, though,
    # and for the sake of consistency, let's keep this function around.)
