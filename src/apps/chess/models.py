from typing import TYPE_CHECKING

from django.db import models

from lib.django_helpers import literal_to_django_choices

from .domain.types import PieceId, PlayerSide, Square

if TYPE_CHECKING:
    pass


class Game(models.Model):
    fen = models.CharField(max_length=150)  # type: str
    pieces_view = models.JSONField()  # type: PiecesView
    active_player = models.CharField(max_length=1, choices=literal_to_django_choices(PlayerSide))  # type: PlayerSide
    bot_side = models.CharField(
        max_length=1, choices=literal_to_django_choices(PlayerSide), null=True
    )  # type: PlayerSide | None

    updated_at = models.DateTimeField(auto_now=True)  # type: datetime

    @property
    def is_versus_bot(self) -> bool:
        return self.bot_side is not None

    def pieces_id_per_square(self) -> dict[Square, PieceId]:
        return {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}


class Team(models.Model):
    # Will be linked to players at some point, but we're user-less for now
    # so we temporarily link them to Games instead
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="teams")  # type: Game


class TeamMember(models.Model):
    first_name = models.CharField(max_length=50)  # type: str
    last_name = models.CharField(max_length=50)  # type: str
    role = models.CharField(max_length=50)  # type: TeamMemberRole

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")  # type: Team

    def __str__(self) -> str:
        return f"{self.role}: {self.first_name} {self.last_name}"

    def public_data(self) -> dict:
        # TODO: move this to a Presenter, since this is View-only
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
        }
