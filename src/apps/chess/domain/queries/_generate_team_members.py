from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ...models import TeamMember
    from ..types import TeamMemberRole

_WHOLE_TEAM_ROLES: tuple["TeamMemberRole", ...] = (
    # fmt: off
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8",
    "r1", "n1", "bb", "q", "k", "bw", "n2", "r2",
    # fmt: on
)


def generate_team_members(*, roles: "Sequence[TeamMemberRole] | None" = None) -> "Sequence[TeamMember]":
    from ._generate_team_member import generate_team_member

    roles = roles or _WHOLE_TEAM_ROLES

    result = []
    for role in roles:
        result.append(generate_team_member(role=role))
    return result
