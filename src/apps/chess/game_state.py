from functools import cached_property
from typing import TYPE_CHECKING

import chess

if TYPE_CHECKING:
    from .business_logic import FEN


class GameState:
    def __init__(self, fen: "FEN", id_:str="main"):
        self._chess = chess.Board(fen)
        self.id = id_

    @cached_property
    def pieces(self):
        return {
            chess.square_name(square): piece
            for square, piece in self._chess.piece_map().items()
        }
