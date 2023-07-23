from typing import TYPE_CHECKING

from lib.chess_engines.sunfish import sunfish, tools

if TYPE_CHECKING:
    from apps.chess.domain.types import PlayerSide, Square

# We'll leave some time for the bot to make a move:
# (already pretty long for a CPU-bounded server-side operation 😅)
_SUNFISH_ALLOWED_TIME = 0.05
_searcher = sunfish.Searcher()  # type: ignore


def get_bot_next_move(*, fen: str, bot_side: "PlayerSide") -> "tuple[Square, Square]":
    sunfish_pos = tools.parseFEN(fen)
    _iterations_count, move, _score, _depth = tools.search(_searcher, sunfish_pos, _SUNFISH_ALLOWED_TIME)
    if bot_side == "b":
        # Quoting Sunfish:
        # > The black player moves from a rotated position, so we have to
        # > 'back rotate' the move before printing it.
        move = 119 - move[0], 119 - move[1]
    from_square, to_square = sunfish.render(move[0]), sunfish.render(move[1])  # type: ignore
    return from_square, to_square
