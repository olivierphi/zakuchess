from contextlib import nullcontext as noraise
from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ValidationError

from ..models import DailyChallengeStatus

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from ..models import DailyChallenge


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("solution", "context", "expected_moves_count"),
    [
        ("f7f8,a8a7,f8d6", noraise(), 2),
        ("f7f8,a8a7,f8d6,a6a5", pytest.raises(ValidationError), None),
        ("f7f8,a8a7,f8d6,a6a5,h2g1", noraise(), 3),
        ("f7f8,a8a7,f8d6,a6a5,h2g1,b7b6", pytest.raises(ValidationError), None),
        ("f7f8,a8a7,f8d6,a6a5,h2g1,b7b6,d6b6", noraise(), 4),
        ("f7f8,a8a7,f8d6,a6a5,h2g1,b7b6,d6b6,a7a8,b6a7", noraise(), 5),
    ],
)
def test_solution_turns_counter_computation(
    challenge_minimalist: "DailyChallenge",
    solution: str,
    context: "AbstractContextManager",
    expected_moves_count: int | None,
):
    assert challenge_minimalist.solution_turns_count == 1

    challenge_minimalist.solution = solution
    challenge_minimalist.status = DailyChallengeStatus.PUBLISHED  # type: ignore
    with context:
        challenge_minimalist.clean()
    if expected_moves_count:
        assert challenge_minimalist.solution_turns_count == expected_moves_count
