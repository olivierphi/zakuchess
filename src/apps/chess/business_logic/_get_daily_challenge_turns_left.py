from typing import TYPE_CHECKING

from .daily_challenge import MAXIMUM_TURNS_PER_CHALLENGE, ChallengeTurnsState

if TYPE_CHECKING:
    from .daily_challenge import PlayerGameState


def get_daily_challenge_turns_state(game_state: "PlayerGameState") -> ChallengeTurnsState:
    turns_left = MAXIMUM_TURNS_PER_CHALLENGE - game_state["turns_counter"]
    percentage_left = round(turns_left / MAXIMUM_TURNS_PER_CHALLENGE * 100)
    game_over = turns_left <= 0

    return ChallengeTurnsState(
        attempts_counter=game_state["attempts_counter"],
        turns_total=MAXIMUM_TURNS_PER_CHALLENGE,
        turns_left=turns_left,
        percentage_left=percentage_left,
        game_over=game_over,
    )
