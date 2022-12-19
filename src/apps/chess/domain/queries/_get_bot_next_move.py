from typing import TYPE_CHECKING

from lib.chess_engines.sunfish import sunfish, tools

if TYPE_CHECKING:
    from apps.chess.domain.types import PlayerSide, Square

# we'll leave 0.1 seconds for the bot to make a move: (which is already pretty long for a CPU-bounded server-side operation 😅)
_SUNFISH_ALLOWED_TIME = 0.1
_searcher = sunfish.Searcher()


def get_bot_next_move(*, fen: str, bot_side: "PlayerSide") -> "tuple[Square, Square]":
    sunfish_pos = tools.parseFEN(fen)
    move, _score, _depth = tools.search(_searcher, sunfish_pos, 0.1)
    if bot_side == "b":
        # Quoting Sunfish:
        # > The black player moves from a rotated position, so we have to
        # > 'back rotate' the move before printing it.
        move = 119 - move[0], 119 - move[1]
    from_square, to_square = sunfish.render(move[0]), sunfish.render(move[1])
    return from_square, to_square
