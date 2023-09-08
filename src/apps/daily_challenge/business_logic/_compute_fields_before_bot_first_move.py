from typing import TYPE_CHECKING

from apps.chess.helpers import uci_move_squares

from ...chess.business_logic import calculate_fen_before_move
from ..consts import BOT_SIDE

if TYPE_CHECKING:
    from ..models import DailyChallenge


def compute_fields_before_bot_first_move(
    challenge: "DailyChallenge",
) -> None:
    """
    Set the `*_before_bot_first_move` fields on the given challenge models,
    from the value of the other fields.
    """
    # `fen_before_bot_first_move` field:
    challenge.fen_before_bot_first_move = calculate_fen_before_move(
        fen_after_move=challenge.fen,
        move_uci=challenge.bot_first_move,
        moving_player_side=BOT_SIDE,
    )

    # `piece_role_by_square_before_bot_first_move` field:
    bot_from, bot_to = uci_move_squares(challenge.bot_first_move)
    piece_role_by_square = challenge.piece_role_by_square.copy()
    piece_role_by_square[bot_from] = piece_role_by_square[bot_to]
    del piece_role_by_square[bot_to]
    challenge.piece_role_by_square_before_bot_first_move = piece_role_by_square
