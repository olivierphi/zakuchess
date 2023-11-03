from typing import TYPE_CHECKING

import chess
from django.core.exceptions import ValidationError
from django.db import models

from apps.chess.types import PlayerSide
from lib.django_helpers import literal_to_django_choices

from .consts import BOT_SIDE, FACTIONS, PLAYER_SIDE

if TYPE_CHECKING:
    from datetime import datetime

    from apps.chess.types import FEN, Factions, GameTeams, PieceRoleBySquare, Square

_PLAYER_SIDE_CHOICES = literal_to_django_choices(PlayerSide)  # type: ignore
_FEN_MAX_LEN = (
    90  # @link https://chess.stackexchange.com/questions/30004/longest-possible-fen
)


class DailyChallengeStatus(models.IntegerChoices):
    PENDING = 0, "pending"
    PUBLISHED = 1, "published"
    ARCHIVED = 2, "archived"


class DailyChallenge(models.Model):
    # ---
    # Let's start with some metadata:
    # This "lookup_key" will be the date of the challenge, e.g. "2023-08-28".
    # But in some cases we also want to have non-date ids, so let's use a CharField
    # (and we're using SQLite, so we can't use "real" date functions anyway)
    lookup_key: str = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        help_text="e.g. '2021-10-01', or just '10-01' for challenges "
        "that can be re-used from a year to the next",
    )
    source: str = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        help_text="e.g. 'lichess-0009B'",
    )
    status: DailyChallengeStatus = models.IntegerField(
        choices=DailyChallengeStatus.choices, default=DailyChallengeStatus.PENDING
    )
    created_at: "datetime" = models.DateTimeField(auto_now_add=True)
    updated_at: "datetime" = models.DateTimeField(auto_now=True)
    # ---
    # The following 2 fields carry the state of the game we want
    # the daily challenge to start with...
    fen: "FEN" = models.CharField(max_length=_FEN_MAX_LEN)
    piece_role_by_square: "PieceRoleBySquare|None" = models.JSONField(
        null=True, editable=False
    )
    # ---
    # Mandatory fields for a published challenge:
    bot_first_move: str | None = models.CharField(
        null=True, max_length=5, help_text="uses UCI notation, e.g. 'e2e4'"
    )
    intro_turn_speech_square: "Square|None" = models.CharField(null=True, max_length=2)
    starting_advantage: int | None = models.IntegerField(
        null=True,
        help_text="positive number means the human player has an advantage, "
        "negative number means the bot has an advantage",
    )
    # ---
    # Fields that are inferred from the above fields:
    # We want the bot to play first, in a deterministic way,
    # so we also need to store the state of the game before that first move.
    fen_before_bot_first_move: "FEN|None" = models.CharField(
        max_length=_FEN_MAX_LEN, null=True, editable=False
    )
    piece_role_by_square_before_bot_first_move: "PieceRoleBySquare|None" = (
        models.JSONField(null=True, editable=False)
    )
    teams: "GameTeams|None" = models.JSONField(null=True, editable=False)
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
        # FEN normalisation:
        chess_board = chess.Board(self.fen)
        chess_board.turn = chess.WHITE  # always starts with the "w" player
        self.fen = chess_board.fen()

        if self.status == DailyChallengeStatus.PUBLISHED:
            self._check_mandatory_fields_for_published_daily_challenge()
            self._set_inferred_fields_for_published_daily_challenge(chess_board)

        super().clean()

    def _check_mandatory_fields_for_published_daily_challenge(self) -> None:
        errors: dict[str, str] = {}
        err_msg = "This field is required for a published Challenge."
        if not self.bot_first_move:
            errors["bot_first_move"] = err_msg
        if not self.intro_turn_speech_square:
            errors["intro_turn_speech_square"] = err_msg
        if not self.starting_advantage:
            errors["starting_advantage"] = err_msg
        if errors:
            raise ValidationError(errors)

    def _set_inferred_fields_for_published_daily_challenge(
        self, chess_board: chess.Board
    ) -> None:
        from apps.daily_challenge.business_logic import (
            compute_fields_before_bot_first_move,
            set_daily_challenge_teams_and_pieces_roles,
        )

        teams, piece_role_by_square = set_daily_challenge_teams_and_pieces_roles(
            fen=self.fen
        )
        self.teams = teams
        self.piece_role_by_square = piece_role_by_square

        # Set `*_before_bot_first_move` fields. Can raise validation errors.
        try:
            compute_fields_before_bot_first_move(self)
        except ValueError as exc:
            raise ValidationError({"bot_first_move": exc}) from exc

        # Checks `intro_turn_speech_square` field.
        if not self.intro_turn_speech_square:
            raise ValidationError(
                {"intro_turn_speech_square": "This field is required."}
            )
        piece_at_square = chess_board.piece_at(
            chess.parse_square(self.intro_turn_speech_square)
        )
        if not piece_at_square or piece_at_square.color != chess.WHITE:
            raise ValidationError(
                {
                    "intro_turn_speech_square": f"'{self.intro_turn_speech_square}' is not a valid 'w' square"
                }
            )
