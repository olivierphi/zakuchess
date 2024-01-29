from typing import TYPE_CHECKING

from ..consts import MAXIMUM_TURNS_PER_CHALLENGE
from ..models import ChallengeTurnsState

if TYPE_CHECKING:
    from ..models import PlayerGameState


def get_daily_challenge_turns_state(
    game_state: "PlayerGameState",
) -> ChallengeTurnsState:
    turns_left = MAXIMUM_TURNS_PER_CHALLENGE - game_state.turns_counter
    percentage_left = round(turns_left / MAXIMUM_TURNS_PER_CHALLENGE * 100)
    time_s_up = turns_left <= 0

    return ChallengeTurnsState(
        attempts_counter=game_state.attempts_counter,
        current_attempt_turns=game_state.current_attempt_turns_counter,
        turns_total=MAXIMUM_TURNS_PER_CHALLENGE,
        turns_left=turns_left,
        percentage_left=percentage_left,
        time_s_up=time_s_up,
    )
