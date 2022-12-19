from typing import TYPE_CHECKING

from apps.chess.models import Game

if TYPE_CHECKING:
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
        "w": {member.role: member.public_data() for member in team_w.members.all()},
        "b": {member.role: member.public_data() for member in team_b.members.all()},
    }
