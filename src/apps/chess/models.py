from typing import TYPE_CHECKING, Annotated

from django.db import models

from lib.django_helpers import literal_to_django_choices

from .domain.types import PlayerSide

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager



class Game(models.Model):
    fen = models.CharField(max_length=150)
    piece_role_by_square = Annotated["PieceRoleBySquare", models.JSONField()]
    active_player = Annotated[
        "PlayerSide", models.CharField(max_length=1, choices=literal_to_django_choices(PlayerSide))
    ]
    bot_side = Annotated[
        "PlayerSide | None", models.CharField(max_length=1, choices=literal_to_django_choices(PlayerSide), null=True)
    ]

    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        teams = RelatedManager["Team"]()

    @property
    def is_versus_bot(self) -> bool:
        return self.bot_side is not None


class Team(models.Model):
    # Will be linked to players at some point, but we're user-less for now
    # so we temporarily link them to Games instead
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="teams")

    if TYPE_CHECKING:
        members = RelatedManager["TeamMember"]()


class TeamMember(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = Annotated["PieceRole", models.CharField(max_length=50)]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")

    def __str__(self) -> str:
        return f"{self.role}: {self.first_name} {self.last_name}"
