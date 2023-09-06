from typing import TYPE_CHECKING

from django.db import models

from lib.django_helpers import literal_to_django_choices

from .business_logic import daily_challenge
from .business_logic.types import PlayerSide

if TYPE_CHECKING:
    from .business_logic.types import FEN, Factions, GameTeams, PieceRoleBySquare

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
    # The following 2 fields carry the state of the game we want the daily challenge to start with...
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
        max_length=5
    )  # uses UCI notation, e.g. "e2e4"

    def __str__(self) -> str:
        return f"{self.id}: {self.fen}"

    @property
    def my_side(self) -> PlayerSide:
        return daily_challenge.PLAYER_SIDE

    @property
    def bot_side(self) -> PlayerSide:
        return daily_challenge.BOT_SIDE

    @property
    def factions(self) -> "Factions":
        return daily_challenge.FACTIONS

    def clean(self) -> None:
        from .business_logic import (
            compute_daily_challenge_before_bot_first_move_fields,
            compute_daily_challenge_teams_and_pieces_roles,
        )

        teams, piece_role_by_square = compute_daily_challenge_teams_and_pieces_roles(
            fen=self.fen
        )
        self.teams = teams
        self.piece_role_by_square = piece_role_by_square

        compute_daily_challenge_before_bot_first_move_fields(self)

        super().clean()
