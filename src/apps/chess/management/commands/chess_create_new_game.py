import time
from typing import TYPE_CHECKING

import chess
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from ...domain.consts import PLAYER_SIDES
from ...domain.mutations import create_new_game

if TYPE_CHECKING:
    from ...domain.types import FEN, PlayerSide


def fen_input(fen: str) -> "FEN":
    chess.Board(fen=fen)  # will raise ValueError if invalid
    return fen


class Command(BaseCommand):
    help = "Creates a Game."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fen",
            type=fen_input,
            help="The FEN to use for the new Game, rather than the classic chess starting position.",
        )
        parser.add_argument(
            "--bot-side",
            choices=PLAYER_SIDES,
            help="w|b. The side the bot should play. If not specified, the bot will not play.",
        )

    def handle(self, *args, fen: "FEN | None", bot_side: "PlayerSide | None", **options):
        start_time = time.monotonic()
        game = create_new_game(fen=fen, bot_side=bot_side)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created Game with ID {game.id} in {time.monotonic() - start_time:.2f}s.")
        )

        allowed_host = settings.ALLOWED_HOSTS[0]
        allowed_host = "http://127.0.0.01:8000" if allowed_host == "*" else f"https://{allowed_host}"
        self.stdout.write(f"{allowed_host}{reverse('chess:game_view', args=[game.id])}")
