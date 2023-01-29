from typing import TYPE_CHECKING, cast

from apps.chess.models import Game

from ..helpers import team_member_role_from_piece_role

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.chess.domain.types import PlayerSide, TeamMemberRole
    from apps.chess.models import TeamMember


def get_team_members_by_role_by_side(*, game: Game) -> "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]":
    team_w, team_b = (
        # TODO: use Players to know which team is which... once we do have Players ^^
        game.teams.all()
        .prefetch_related("members")
        .order_by("id")
    )

    return {
        "w": {
            team_member_role_from_piece_role(member.role): member
            for member in cast("Sequence[TeamMember]", team_w.members.all())
        },
        "b": {
            team_member_role_from_piece_role(member.role): member
            for member in cast("Sequence[TeamMember]", team_b.members.all())
        },
    }
