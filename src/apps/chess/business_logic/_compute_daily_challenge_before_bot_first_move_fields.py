from typing import TYPE_CHECKING

from ..helpers import uci_move_squares
from . import daily_challenge

if TYPE_CHECKING:
    from ..models import DailyChallenge


def compute_daily_challenge_before_bot_first_move_fields(challenge: "DailyChallenge") -> None:
    """
    Set the `*_before_bot_first_move` fields on the given challenge models,
    from the value of the other fields.
    """
    from . import calculate_fen_before_bot_first_move

    # `fen_before_bot_first_move` field:
    challenge.fen_before_bot_first_move = calculate_fen_before_bot_first_move(
        fen_after_first_move=challenge.fen,
        bot_first_move=challenge.bot_first_move,
        bot_side=daily_challenge.BOT_SIDE,
    )

    # `piece_role_by_square_before_bot_first_move` field:
    bot_from, bot_to = uci_move_squares(challenge.bot_first_move)
    piece_role_by_square = challenge.piece_role_by_square.copy()
    piece_role_by_square[bot_from] = piece_role_by_square[bot_to]
    del piece_role_by_square[bot_to]
    challenge.piece_role_by_square_before_bot_first_move = piece_role_by_square
