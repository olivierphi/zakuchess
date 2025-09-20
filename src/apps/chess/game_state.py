from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import chess

if TYPE_CHECKING:
    from .business_logic import FEN, BoardOrientation


class GameState:
    def __init__(
        self, fen: "FEN", *, board_orientation: BoardOrientation, id_: str = "main"
    ):
        self._chess = chess.Board(fen)
        self.board_orientation = board_orientation
        self.id = id_

    @cached_property
    def pieces(self):
        # TODO: improve this
        return {
            chess.square_name(square): piece
            for square, piece in self._chess.piece_map().items()
        }

    @cached_property
    def legal_moves(self):
        # TODO: improve this
        return tuple(
            (chess.square_name(move.from_square), chess.square_name(move.to_square))
            for move in self._chess.legal_moves
        )
