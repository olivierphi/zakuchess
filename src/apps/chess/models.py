from typing import TYPE_CHECKING

from django.db import models

from lib.django_helpers import literal_to_django_choices

from .domain.types import PlayerSide

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from .domain.types import FEN, PieceRole, PieceRoleBySquare

_PLAYER_SIDE_CHOICES = literal_to_django_choices(PlayerSide)  # type: ignore


class Game(models.Model):
    fen: "FEN" = models.CharField(max_length=150)
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
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    role: "PieceRole" = models.CharField(max_length=50)

    team: Team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")

    if TYPE_CHECKING:
        id: int
        team_id: int

    def __str__(self) -> str:
        return f"{self.role}: {self.first_name} {self.last_name}"
