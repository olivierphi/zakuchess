import chess
from django.db import models

from .domain.queries import get_chess_board_state
from .domain.types import ChessBoardState, PiecesView


class Game(models.Model):
    fen = models.CharField(max_length=150)
    pieces_view = models.JSONField()  # type: PiecesView

    def get_board_state(self) -> ChessBoardState:
        pieces_ids_per_square = {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}
        return get_chess_board_state(fen=self.fen, pieces_ids_per_square=pieces_ids_per_square)

    def get_chess_board(self) -> chess.Board:
        return chess.Board(fen=self.fen)
