import chess
from django.db import models

from lib.django_helpers import literal_to_django_choices

from .domain.queries import get_chess_board_state
from .domain.types import ChessBoardState, PlayerSide


class Game(models.Model):
    fen = models.CharField(max_length=150)  # type: str
    pieces_view = models.JSONField()  # type: PiecesView
    active_player = models.CharField(max_length=1, choices=literal_to_django_choices(PlayerSide))  # type: PlayerSide
    bot_side = models.CharField(
        max_length=1, choices=literal_to_django_choices(PlayerSide), null=True
    )  # type: PlayerSide | None

    def get_board_state(self) -> ChessBoardState:
        pieces_ids_per_square = {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}
        return get_chess_board_state(fen=self.fen, pieces_ids_per_square=pieces_ids_per_square)

    def get_chess_board(self) -> chess.Board:
        return chess.Board(fen=self.fen)

    @property
    def is_versus_bot(self) -> bool:
        return self.bot_side is None
