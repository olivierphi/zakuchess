from random import sample
from typing import TYPE_CHECKING

from ...models import TeamMember
from ..data.team_member_names import FIRST_NAMES, LAST_NAMES

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..types import TeamMemberRole


def generate_team_members(*, roles: "Sequence[TeamMemberRole]") -> "Sequence[TeamMember]":
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
