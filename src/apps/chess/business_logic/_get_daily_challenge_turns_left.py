from typing import TYPE_CHECKING, NamedTuple

from .daily_challenge import MAXIMUM_TURNS_PER_CHALLENGE

if TYPE_CHECKING:
    from .daily_challenge import PlayerGameState


class ChallengeTurnsLeftResult(NamedTuple):
    turns_total: int
    turns_left: int
    percentage_left: int
    is_challenge_over: bool


def get_daily_challenge_turns_left(game_state: "PlayerGameState") -> ChallengeTurnsLeftResult:
    turns_left = MAXIMUM_TURNS_PER_CHALLENGE - game_state["turns_counter"]
    percentage_left = round(turns_left / MAXIMUM_TURNS_PER_CHALLENGE * 100)
    is_challenge_over = turns_left <= 0

    return ChallengeTurnsLeftResult(
        turns_total=MAXIMUM_TURNS_PER_CHALLENGE,
        turns_left=turns_left,
        percentage_left=percentage_left,
        is_challenge_over=is_challenge_over,
    )
