from typing import TYPE_CHECKING

from .daily_challenge import MAXIMUM_TURNS_PER_CHALLENGE, ChallengeTurnsLeftResult

if TYPE_CHECKING:
    from .daily_challenge import PlayerGameState


def get_daily_challenge_turns_left(game_state: "PlayerGameState") -> ChallengeTurnsLeftResult:
    turns_left = MAXIMUM_TURNS_PER_CHALLENGE - game_state["turns_counter"]
    percentage_left = round(turns_left / MAXIMUM_TURNS_PER_CHALLENGE * 100)
    game_over = turns_left <= 0

    return ChallengeTurnsLeftResult(
        turns_total=MAXIMUM_TURNS_PER_CHALLENGE,
        turns_left=turns_left,
        percentage_left=percentage_left,
        game_over=game_over,
    )
