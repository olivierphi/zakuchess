from random import sample
from typing import TYPE_CHECKING

from ..data.team_member_names import FIRST_NAMES, LAST_NAMES
from ...models import TeamMember

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..types import TeamMemberRole

_WHOLE_TEAM_ROLES: tuple["TeamMemberRole", ...] = (
    # fmt: off
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8",
    "r1", "n1", "bb", "q", "k", "bw", "n2", "r2",
    # fmt: on
)


def generate_team_members(*, roles: "Sequence[TeamMemberRole] | None" = None) -> "Sequence[TeamMember]":
    roles = roles or _WHOLE_TEAM_ROLES

    first_names = sample(FIRST_NAMES, k=len(roles))
    last_names = sample(LAST_NAMES, k=len(roles))

    result = []
    for i, role in enumerate(roles):
        result.append(
            TeamMember(
                first_name=first_names[i],
                last_name=last_names[i],
                role=role,
            )
        )
    return result
