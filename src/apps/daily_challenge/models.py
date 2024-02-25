import datetime as dt
import enum
import math
from typing import TYPE_CHECKING, ClassVar, Literal, Self, TypeAlias

import chess
import msgspec
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.db.models import F
from django.utils.timezone import now

from apps.chess.types import (  # we need real imports on these because they're used by msgspec models
    FEN,
    PieceRoleBySquare,
    PlayerSide,
)
from lib.django_helpers import literal_to_django_choices

from .consts import BOT_SIDE, FACTIONS, PLAYER_SIDE

if TYPE_CHECKING:
    from datetime import datetime

    from apps.chess.types import Factions, GameTeams, Square


GameID: TypeAlias = str

WinsDistributionSlice = Literal[1, 2, 3, 4, 5]
WinsDistribution = dict[Literal[1, 2, 3, 4, 5], int]

_PLAYER_SIDE_CHOICES = literal_to_django_choices(PlayerSide)  # type: ignore
_FEN_MAX_LEN = (
    90  # @link https://chess.stackexchange.com/questions/30004/longest-possible-fen
)

_STATS_FOR_TODAY_EXISTS_CACHE = {
    "KEY_PATTERN": "stats_for_today_exists:{today}",
    "DURATION": 3_600 * 10,  # 10 hours
}


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
    fen_before_bot_first_move: "FEN|None" = models.CharField(
        max_length=_FEN_MAX_LEN, null=True, editable=False
    )
    piece_role_by_square_before_bot_first_move: "PieceRoleBySquare|None" = (
        models.JSONField(null=True, editable=False)
    )
    teams: "GameTeams|None" = models.JSONField(null=True, editable=False)
    intro_turn_speech_text: str = models.CharField(max_length=100, blank=True)
    solution_turns_count: int = models.PositiveSmallIntegerField(
        null=True, editable=False
    )

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

        if self.solution:
            # Compute `solution_moves_count` from `solution`
            self.solution_turns_count = math.ceil(self.solution.count(",") / 2) + 1

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


class DailyChallengeStatsManager(models.Manager):

    def increment_today_created_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(created_count=F("created_count") + 1)

    def increment_today_played_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(played_count=F("played_count") + 1)

    def increment_today_turns_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(turns_count=F("turns_count") + 1)

    def increment_today_restarts_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(restarts_count=F("restarts_count") + 1)

    def increment_today_wins_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(wins_count=F("wins_count") + 1)

    def increment_today_see_solution_count(self) -> None:
        self._create_for_today_if_needed()
        self.filter(day=self._today()).update(
            see_solution_count=F("see_solution_count") + 1
        )

    def _create_for_today_if_needed(self) -> None:
        today = self._today()
        cache_key = _STATS_FOR_TODAY_EXISTS_CACHE["KEY_PATTERN"].format(today=today)  # type: ignore[attr-defined]
        if cache.get(cache_key):
            return

        try:
            from .business_logic import get_current_daily_challenge

            self.create(
                day=today,
                challenge=get_current_daily_challenge(),
            )
        except IntegrityError:
            pass  # already exists? Fine :-)

        # We won't check if today's game stats were created again:
        cache.set(cache_key, True, _STATS_FOR_TODAY_EXISTS_CACHE["DURATION"])

    @staticmethod
    def _today() -> dt.date:
        return now().date()


class DailyChallengeStats(models.Model):
    """
    Quick stats about the daily challenges. Doesn't store any data about any players.
    """

    day = models.DateField(unique=True)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    created_count = models.IntegerField(default=0, help_text="Number of games created")
    played_count = models.IntegerField(
        default=0, help_text="Number of games where the player played at least 1 move"
    )
    turns_count = models.IntegerField(
        default=0, help_text="Number of turns played by players"
    )
    restarts_count = models.IntegerField(default=0)
    wins_count = models.IntegerField(default=0)
    see_solution_count = models.IntegerField(default=0)

    objects = DailyChallengeStatsManager()

    class Meta:
        ordering = ("-day",)
        verbose_name = "Daily challenge stats"
        verbose_name_plural = "Daily challenges stats"


@enum.unique
class PlayerGameOverState(enum.IntEnum):
    """
    This is the state of a daily challenge,
    stored within a PlayerSessionContent (so, in a cookie).
    """

    # The player has not won yet, and has not lost yet.
    # They can still play.
    PLAYING = 0
    # The player has won the challenge.
    WON = 1
    # The player has lost the challenge.
    LOST = -1


class PlayerGameState(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # Let's make the cookie content a bit shorter, with shorter field names
        "attempts_counter": "ac",
        "turns_counter": "tc",
        "current_attempt_turns_counter": "catc",
        "fen": "f",
        "piece_role_by_square": "prbs",
        "moves": "m",
        "game_over": "go",
        "solution_index": "sol",
    },
):
    """
    This is the state of a daily challenge,
    stored within a PlayerSessionContent (so, in a cookie).

    Counters are zero-based.
    """

    # the number of attempts for today's challenge - 0-based:
    attempts_counter: int
    # the sum of number of turns for all today's attempts:
    turns_counter: int
    # the number of turns for the current attempt:
    current_attempt_turns_counter: int
    fen: FEN
    piece_role_by_square: PieceRoleBySquare
    # Each move is 4 more chars added there (UCI notation).
    # These are the moves *of the current attempt* only.
    moves: str
    game_over: "PlayerGameOverState" = PlayerGameOverState.PLAYING
    # is a half-move index when the player gave up to see the solution:
    solution_index: int | None = None

    def replace(self, **kwargs) -> Self:
        return msgspec.structs.replace(self, **kwargs)


class PlayerStats(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # ditto
        "games_count": "gc",
        "win_count": "wc",
        "current_streak": "cs",
        "max_streak": "ms",
        "last_played": "lp",
        "last_won": "lw",
        "wins_distribution": "wd",
    },
):
    """
    This is the stats of the player for daily challenges,
    stored within a PlayerSessionContent (so, in a cookie).
    """

    WINS_DISTRIBUTION_SLICE_COUNT: ClassVar[int] = 5

    games_count: int = 0
    win_count: int = 0
    current_streak: int = 0
    max_streak: int = 0
    last_played: dt.date | None = None
    last_won: dt.date | None = None
    wins_distribution: WinsDistribution = msgspec.field(
        default_factory=lambda: {
            1: 0,  # challenges won on the 1st attempt
            2: 0,  # challenges won in the 2nd attempt
            3: 0,  # ditto for 3rd attempt
            4: 0,  # ditto for 4th attempt
            5: 0,  # won in 5 attempts or more
        }
    )

    @property
    def win_rate(self) -> int:
        """
        Because it's frustrating to see 99% when one lost only 1 game amongst many wins,
        this win rate is rounded up.
        """
        if self.games_count == 0 or self.win_count == 0:
            return 0
        return math.ceil(self.win_count / self.games_count * 100)


class PlayerSessionContent(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # ditto
        "encoding_version": "ev",
        "games": "g",
        "stats": "s",
    },
):
    """
    This is the whole content of the session cookie for the player.
    """

    encoding_version: int = 1
    games: dict[GameID, PlayerGameState]
    stats: PlayerStats

    def to_cookie_content(self) -> str:
        return msgspec.json.encode(self).decode()

    @classmethod
    def from_cookie_content(cls, cookie_content: str) -> Self:
        return msgspec.json.decode(cookie_content.encode(), type=cls)
