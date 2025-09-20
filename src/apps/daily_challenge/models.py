from __future__ import annotations

import math
from typing import TYPE_CHECKING

import chess
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

if TYPE_CHECKING:
    import datetime as dt

    from apps.chess.types import (
        FEN,
        CharacterIdBySquare,
        GameTeamsDict,
        MoveUCI,
        Square,
    )

_FEN_MAX_LEN = (
    90  # @link https://chess.stackexchange.com/questions/30004/longest-possible-fen
)


class DailyChallenge(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, "pending"
        PUBLISHED = 1, "published"
        ARCHIVED = 2, "archived"

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
    status: Status = models.IntegerField(choices=Status, default=Status.PENDING)
    created_at: dt.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: dt.datetime = models.DateTimeField(auto_now=True)

    # ---
    # The following 2 fields carry the state of the game we want
    # the daily challenge to start with...
    fen: FEN = models.CharField(max_length=_FEN_MAX_LEN)
    character_id_by_square: CharacterIdBySquare | None = models.JSONField(
        # this one is set from the FEN in our `clean()` method:
        null=True,
        editable=False,
    )

    # ---
    # Mandatory fields for a published challenge:
    bot_first_move: MoveUCI | None = models.CharField(
        null=True, max_length=5, help_text="uses UCI notation, e.g. 'e2e4'"
    )
    bot_depth: int = models.PositiveSmallIntegerField(
        default=1,
        help_text="The depth of the bot's search. 1 is a good value for an 'easy enough' daily challenge.",
    )
    # The following value is the depth we want the bot to calculate its moves with
    # when it simulates the human player's turn, while we're building the solution:
    player_simulated_depth: int = models.PositiveSmallIntegerField(
        default=5,
        help_text="The depth of the player's simulated search. "
        "5 is a good value for modeling a 'casual' chess player (like myself ^_^).",
    )
    intro_turn_speech_square: Square | None = models.CharField(null=True, max_length=2)
    starting_advantage: int | None = models.IntegerField(
        null=True,
        help_text="positive number means the human player has an advantage, "
        "negative number means the bot has an advantage",
    )
    solution: str = models.CharField(
        max_length=150,
        blank=True,
        help_text="A comma-separated list of UCI moves",
        validators=[
            RegexValidator(r"^(?:[a-h][1-8][a-h][1-8],){1,}[a-h][1-8][a-h][1-8]$")
        ],
    )

    # ---
    # Fields that are inferred from the above fields:
    # We want the bot to play first, in a deterministic way,
    # so we also need to store the state of the game before that first move.
    fen_before_bot_first_move: FEN | None = models.CharField(
        max_length=_FEN_MAX_LEN, null=True, editable=False
    )
    character_id_by_square_before_bot_first_move: CharacterIdBySquare | None = (
        models.JSONField(null=True, editable=False)
    )
    teams: GameTeamsDict | None = models.JSONField(null=True, editable=False)
    intro_turn_speech_text: str = models.CharField(max_length=100, blank=True)
    solution_turns_count: int = models.PositiveSmallIntegerField(
        null=True, editable=False
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.fen}"

    def clean(self) -> None:
        # FEN normalisation:
        chess_board = chess.Board(self.fen)
        # daily challenges always start with the "w" player:
        chess_board.turn = chess.WHITE
        self.fen = chess_board.fen()

        if self.solution:
            # Compute `solution_moves_count` from `solution`
            self.solution_turns_count = math.ceil(self.solution.count(",") / 2) + 1

        if self.status == self.Status.PUBLISHED:
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
        if (
            not self.solution
            or len(self.solution) < 8
            # It should always end with a move from the player:
            or self.solution.count(",") % 2 != 0
        ):
            errors["solution"] = err_msg
        if errors:
            raise ValidationError(errors)

    def _set_inferred_fields_for_published_daily_challenge(
        self, chess_board: chess.Board
    ) -> None:
        from .business_logic import (
            compute_fields_before_bot_first_move,
            init_daily_challenge_teams,
        )

        teams, character_id_by_square = init_daily_challenge_teams(fen=self.fen)
        self.teams = teams.to_dict()
        self.character_id_by_square = character_id_by_square

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
                    "intro_turn_speech_square": f"'{self.intro_turn_speech_square}'"
                    " is not a valid 'w' square"
                }
            )
