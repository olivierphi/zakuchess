from typing import TYPE_CHECKING

from ..models import ChallengeTurnsState

if TYPE_CHECKING:
    from ..models import DailyChallenge, PlayerGameState


def get_daily_challenge_turns_state(
    *,
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
) -> ChallengeTurnsState:
    turns_left = challenge.max_turns_count - game_state.turns_counter
    percentage_left = round(turns_left / challenge.max_turns_count * 100)
    time_s_up = turns_left <= 0

    return ChallengeTurnsState(
        attempts_counter=game_state.attempts_counter,
        current_attempt_turns=game_state.current_attempt_turns_counter,
        turns_total=challenge.max_turns_count,
        turns_left=turns_left,
        percentage_left=percentage_left,
        time_s_up=time_s_up,
    )
