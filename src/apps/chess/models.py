import chess
from django.db import models

from lib.django_helpers import enum_to_django_choices
from .domain.queries import get_chess_board_state
from .domain.types import ChessBoardState, PiecesView, PlayerSide


class Game(models.Model):
    fen = models.CharField(max_length=150)
    pieces_view = models.JSONField()  # type: PiecesView
    active_player = models.CharField(max_length=1, choices=enum_to_django_choices(PlayerSide))
    is_versus_bot = models.BooleanField()

    def get_board_state(self) -> ChessBoardState:
        pieces_ids_per_square = {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}
        return get_chess_board_state(fen=self.fen, pieces_ids_per_square=pieces_ids_per_square)

    def get_chess_board(self) -> chess.Board:
        return chess.Board(fen=self.fen)
