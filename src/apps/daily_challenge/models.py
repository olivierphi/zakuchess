from typing import TYPE_CHECKING

from django.db import models

from apps.chess.types import PlayerSide
from lib.django_helpers import literal_to_django_choices

from .consts import BOT_SIDE, FACTIONS, PLAYER_SIDE

if TYPE_CHECKING:
    from apps.chess.types import FEN, Factions, GameTeams, PieceRoleBySquare, Square

_PLAYER_SIDE_CHOICES = literal_to_django_choices(PlayerSide)  # type: ignore
_FEN_MAX_LEN = (
    90  # @link https://chess.stackexchange.com/questions/30004/longest-possible-fen
)


class DailyChallenge(models.Model):
    # This "id" will be the date of the challenge, e.g. "2023-08-28".
    # But in some cases we also want to have non-date ids, so let's use a CharField
    # (and we're using SQLite, so we can't use "real" date functions anyway)
    id: str = models.CharField(
        primary_key=True, max_length=20
    )  # e.g. "2021-10-01" # noqa: A001
    # The following 2 fields carry the state of the game we want
    # the daily challenge to start with...
    fen: "FEN" = models.CharField(max_length=_FEN_MAX_LEN)
    piece_role_by_square: "PieceRoleBySquare" = models.JSONField(editable=False)
    # ...but as we want the bot to play first, in a deterministic way,
    # we also need to store the state of the game before that first move.
    fen_before_bot_first_move: "FEN" = models.CharField(
        max_length=_FEN_MAX_LEN, editable=False
    )
    piece_role_by_square_before_bot_first_move: "PieceRoleBySquare" = models.JSONField(
        editable=False
    )
    teams: "GameTeams" = models.JSONField(editable=False)
    bot_first_move: str = models.CharField(
        max_length=5, help_text="uses UCI notation, e.g. 'e2e4'"
    )
    intro_turn_speech_square: "Square" = models.CharField(max_length=2)
    intro_turn_speech_text: str = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.id}: {self.fen}"

    @property
    def my_side(self) -> PlayerSide:
        return PLAYER_SIDE

    @property
    def bot_side(self) -> PlayerSide:
        return BOT_SIDE

    @property
    def factions(self) -> "Factions":
        return FACTIONS

    def clean(self) -> None:
        from apps.daily_challenge.business_logic import (
            compute_fields_before_bot_first_move,
            set_daily_challenge_teams_and_pieces_roles,
        )

        teams, piece_role_by_square = set_daily_challenge_teams_and_pieces_roles(
            fen=self.fen
        )
        self.teams = teams
        self.piece_role_by_square = piece_role_by_square

        compute_fields_before_bot_first_move(self)

        super().clean()
