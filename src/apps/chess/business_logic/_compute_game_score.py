import logging
from typing import TYPE_CHECKING

import chess
import chess.engine
from django.conf import settings

if TYPE_CHECKING:
    from ..types import FEN

_logger = logging.getLogger(__name__)


def compute_game_score(
    *, chess_board: chess.Board | None = None, fen: "FEN | None" = None
) -> int:
    """
    Returns the advantage of the white player, in centipawns.
    ⚠ This function is blocking, and it can take up to 0.1 second to return, so it
    should only be called from operations taking place in the Django Admin!
    """
    assert chess_board or fen, "Either `chess_board` or `fen` must be provided."

    if not chess_board:
        chess_board = chess.Board(fen)

    _logger.info(
        "Computing game score for FEN: %s",
        chess_board.fen(),
        extra={
            "Stockfish path": settings.STOCKFISH_PATH,
            "Stockfish time limit": settings.STOCKFISH_TIME_LIMIT,
        },
    )

    try:
        engine = chess.engine.SimpleEngine.popen_uci(settings.STOCKFISH_PATH)
    except chess.engine.EngineTerminatedError as exc:
        _logger.error("Stockfish engine terminated before analyze: %s", exc)
        return 0

    info = engine.analyse(
        chess_board, chess.engine.Limit(time=settings.STOCKFISH_TIME_LIMIT)
    )
    advantage = info["score"].white().score()
    engine.quit()

    return advantage
