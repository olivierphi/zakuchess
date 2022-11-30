import enum
from collections.abc import Sequence


def enum_to_django_choices(enum_class: type[enum.Enum]) -> Sequence[tuple[str, str]]:
    return [(enum_member.name, str(enum_member.value)) for enum_member in enum_class]
