from typing import TYPE_CHECKING

from django.db import models

from lib.django_helpers import literal_to_django_choices

from .domain.types import PlayerSide

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from .domain.dto import GameTeams
    from .domain.types import FEN, PieceRole, PieceRoleBySquare

_PLAYER_SIDE_CHOICES = literal_to_django_choices(PlayerSide)  # type: ignore
_FEN_MAX_LEN = 90  # @link https://chess.stackexchange.com/questions/30004/longest-possible-fen


class DailyChallenge(models.Model):
    # This "id" will be the date of the challenge, e.g. "2023-08-28".
    # But in some cases we also want to have non-date ids, so let's use a CharField
    # (and we're using SQLite, so we can't use "real" date functions anyway)
    id: str = models.CharField(primary_key=True, max_length=20)  # e.g. "2021-10-01" # noqa: A001
    fen: "FEN" = models.CharField(max_length=_FEN_MAX_LEN)
    fen_before_bot_first_move: "FEN" = models.CharField(max_length=_FEN_MAX_LEN, editable=False)
    piece_role_by_square: "PieceRoleBySquare" = models.JSONField(editable=False)
    teams: "GameTeams" = models.JSONField(editable=False)
    bot_first_move: str = models.CharField(max_length=5)  # uses UCI notation, e.g. "e2e4"

    def __str__(self) -> str:
        return f"{self.id}: {self.fen}"


# Game, Team and TeamMember are models we're no longer using since ZakuChess pivoted
# to be a "daily challenge only" game. But we might re-use them in the future, so
# let's keep these models here for now.


class Game(models.Model):
    fen: "FEN" = models.CharField(max_length=_FEN_MAX_LEN)
    piece_role_by_square: "PieceRoleBySquare" = models.JSONField()
    active_player: "PlayerSide" = models.CharField(max_length=1, choices=_PLAYER_SIDE_CHOICES)
    bot_side: "PlayerSide | None" = models.CharField(max_length=1, choices=_PLAYER_SIDE_CHOICES, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        id: int
        teams: RelatedManager["Team"]

    @property
    def is_versus_bot(self) -> bool:
        return self.bot_side is not None


class Team(models.Model):
    # Will be linked to players at some point, but we're user-less for now
    # so we temporarily link them to Games instead
    game: Game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="teams")

    if TYPE_CHECKING:
        id: int
        game_id: int
        members: RelatedManager["TeamMember"]


class TeamMember(models.Model):
    first_name: str = models.CharField(max_length=50, blank=True, null=True)
    last_name: str = models.CharField(max_length=50, blank=True, null=True)
    role: "PieceRole" = models.CharField(max_length=50)

    team: Team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")

    if TYPE_CHECKING:
        id: int
        team_id: int

    def __str__(self) -> str:
        return f"{self.role}: {self.first_name} {self.last_name}"
