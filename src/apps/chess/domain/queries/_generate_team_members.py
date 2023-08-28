from random import sample
from typing import TYPE_CHECKING

from ...models import TeamMember
from ..data.team_member_names import FIRST_NAMES, LAST_NAMES

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..types import TeamMemberRole


def generate_team_members(*, roles: "Sequence[TeamMemberRole]", generate_names: bool) -> "Sequence[TeamMember]":
    if generate_names:
        first_names = sample(FIRST_NAMES, k=len(roles))
        last_names = sample(LAST_NAMES, k=len(roles))
    else:
        first_names = last_names = None  # type: ignore

    result = []
    for role in roles:
        result.append(
            TeamMember(
                role=role,
                first_name=first_names.pop() if first_names is not None else None,
                last_name=last_names.pop() if last_names is not None else None,
            )
        )
    return result
